# React Tips — Reference

Sorgente: Neciu Dan — *"10 React tips I wish someone had told me before I mass-produced bugs"* (2026-03-25)
React docs di riferimento: https://react.dev/learn/you-might-not-need-an-effect

Questo file è una reference per progressive disclosure: caricalo solo quando stai analizzando uno specifico tip e hai bisogno del razionale completo o di esempi canonici.

---

## Indice

- [Tip 1 — Stati entangled → useReducer](#tip-1)
- [Tip 2 — useTransition vs debounce](#tip-2)
- [Tip 3 — State colocation](#tip-3)
- [Tip 4 — useEffect è synchronization](#tip-4)
- [Tip 5 — Stop using index as key](#tip-5)
- [Tip 6 — key prop resets everything](#tip-6)
- [Tip 7 — Il tuo useMemo è overhead](#tip-7)
- [Tip 8 — SRP significa "one reason to change"](#tip-8)
- [Tip 9 — useLayoutEffect elimina il flicker](#tip-9)
- [Tip 10 — Compound Components vs prop soup](#tip-10)
- [Trasversali fondamentali](#trasversali)

---

## Tip 1 — Stati entangled → useReducer {#tip-1}

**Rule**: quando più `useState` devono cambiare insieme per restare in uno stato valido, sostituirli con `useReducer`. Un singolo `dispatch` produce uno stato garantito coerente.

**Why it matters**: React non sa che `isLoading`, `error` e `data` sono legati. Ogni setter è indipendente. Se dimentichi di azzerare `error` al successo, ottieni `not-loading + error + data` contemporaneamente — uno stato impossibile che la UI non è progettata per gestire. Il bug può passare inosservato settimane perché si manifesta solo in race conditions specifiche.

**Bad**
```jsx
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState(null);
const [post, setPost] = useState(null);

// Tre setter separati → è facile dimenticarne uno
fetch('/api/post').then(data => {
  setIsLoading(false);
  // dimenticato: setError(null) → stato impossibile se c'era errore prima
  setPost(data);
});
```

**Good**
```jsx
function fetchReducer(state, action) {
  switch (action.type) {
    case 'FETCH_SUCCESS':
      return { isLoading: false, error: null, post: action.payload };
    case 'FETCH_ERROR':
      return { isLoading: false, error: 'Something went wrong!', post: null };
    default:
      return state;
  }
}

const [state, dispatch] = useReducer(fetchReducer, {
  isLoading: true, error: null, post: null,
});

// Un dispatch, uno stato garantito valido
dispatch({ type: 'FETCH_SUCCESS', payload: data });
```

**Edge cases / quando NON applicare**
- Se gli state sono davvero indipendenti (non cambiano insieme), `useState` separati sono corretti.
- La regola non riguarda quanti `useState` hai — riguarda quanto sono *entangled*: se cambiarli in ordine sbagliato produce uno stato inconsistente, è il momento di `useReducer`.

**Context adjustments**
- Il finding è valido anche con Zustand, Redux, Jotai: impossible state può emergere in qualsiasi store. Con Redux, il pattern è identico (reducer che gestisce transizioni valide).

---

## Tip 2 — useTransition vs debounce {#tip-2}

**Rule**: `useTransition` è per lavoro CPU-bound (filtraggio in-memory di liste grandi). `debounce` è per lavoro network-bound (evitare troppe chiamate API). Confondere i due non risolve il bottleneck reale.

**Why it matters**: `useTransition` non aiuta se il problema è il network — il fetch parte comunque, solo il render viene posticipato. `debounce` non aiuta se il problema è il render — la lista continua a bloccare il thread quando arriva il risultato.

**Bad (useTransition per network)**
```jsx
// ❌ useTransition non aiuta: il bottleneck è il fetch, non il render
const [isPending, startTransition] = useTransition();
const handleChange = (e) => {
  startTransition(() => {
    fetchFromAPI(e.target.value).then(setResults);
  });
};
```

**Good (usare il tool giusto)**
```jsx
// Filtraggio in-memory (CPU-bound) → useTransition
const [query, setQuery] = useState('');
const [filteredItems, setFilteredItems] = useState(items);
const [isPending, startTransition] = useTransition();

const handleChange = (e) => {
  setQuery(e.target.value);              // alta priorità: input responsivo
  startTransition(() => {
    setFilteredItems(filterItems(e.target.value)); // bassa priorità: render posticipato
  });
};

// Fetch API (network-bound) → debounce
const debouncedSearch = useMemo(
  () => debounce((q) => fetchFromAPI(q).then(setResults), 300),
  []
);
```

**Edge cases**
- Lista grande in-memory + debounce: funziona ma non è ottimale — ogni keystroke che passa il debounce blocca il thread. `useTransition` è meglio.
- Se usi React Query con `keepPreviousData`, il debounce è già gestito dalla libreria.

---

## Tip 3 — State colocation {#tip-3}

**Rule**: prima di aggiungere `React.memo`, verifica se lo state può semplicemente scendere nell'albero. Se uno state è usato solo da una sotto-sezione dell'albero, tenerlo nel parent causa re-render inutili dei siblings.

**Why it matters**: quando chiami un setter in un parent, React re-renderizza il parent E tutti i suoi children (anche quelli che non usano quello state). `React.memo` è un cerotto — la colocation risolve il problema alla radice.

**Bad**
```jsx
function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  return (
    <div>
      <SearchBox value={searchTerm} onChange={setSearchTerm} />
      <SearchResults query={searchTerm} />
      <AnalyticsChart /> {/* re-render ad ogni keystroke! Non usa searchTerm */}
    </div>
  );
}
```

**Good**
```jsx
function Dashboard() {
  return (
    <div>
      <SearchFeature />
      <AnalyticsChart /> {/* il parent non si re-renderizza più */}
    </div>
  );
}

function SearchFeature() {
  const [searchTerm, setSearchTerm] = useState('');
  return (
    <>
      <SearchBox value={searchTerm} onChange={setSearchTerm} />
      <SearchResults query={searchTerm} />
    </>
  );
}
```

**Edge cases / quando NON applicare**
- Se lo state deve essere accessibile da siblings lontani nell'albero, la colocation non è praticabile → Context o state manager.
- Se il componente "pesante" è un figlio diretto del parent che cambia state, considera `children` prop come optimization alternativa (children non re-renderizza se la reference non cambia).

**Context adjustments**
- Skip questo finding se il valore è chiaramente in un global store (Zustand, Redux) — è già "colocato" nel senso architetturale.
- Questo è un `SUGGEST ONLY` — richiede refactoring dell'albero componenti.

---

## Tip 4 — useEffect è synchronization {#tip-4}

**Rule**: `useEffect` serve per sincronizzare un side effect con valori reattivi — non come `componentDidMount`. Il mental model corretto è: "mantieni questo in sync con queste dipendenze."

**Why it matters**: con il mental model sbagliato si usano useEffect per cose che non dovrebbero essere effect: derivare state da altro state (può essere calcolato in render), o fare fetch senza gestire race conditions/cleanup.

### T4a — Derivare state da altro state

**Bad**
```jsx
const [items, setItems] = useState([...]);
const [filteredItems, setFilteredItems] = useState([]);

// ❌ effect inutile: filteredItems può essere calcolato direttamente
useEffect(() => {
  setFilteredItems(items.filter(i => i.active));
}, [items]);
```

**Good**
```jsx
const [items, setItems] = useState([...]);
// ✅ calcolo diretto in render (o useMemo se costoso)
const filteredItems = items.filter(i => i.active);
```

### T4b — Data fetching

**Bad**
```jsx
// ❌ nessuna cancellazione, nessun caching, race condition se userId cambia velocemente
useEffect(() => {
  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(setUser);
}, [userId]);
```

**Good (con React Query)**
```jsx
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});
```

**Good (senza libreria — AbortController)**
```jsx
useEffect(() => {
  let cancelled = false;
  async function load() {
    const res = await fetch(`/api/users/${userId}`);
    const data = await res.json();
    if (!cancelled) setUser(data);
  }
  load();
  return () => { cancelled = true; };
}, [userId]);
```

### T4c — Cleanup mancante

**Bad**
```jsx
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (e) => setMessages(prev => [...prev, e.data]);
  // ❌ nessun cleanup: il WebSocket resta aperto dopo unmount
}, [url]);
```

**Good**
```jsx
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (e) => setMessages(prev => [...prev, e.data]);
  return () => ws.close(); // ✅ cleanup su unmount o cambio di url
}, [url]);
```

**Usi legittimi di useEffect**: sync con localStorage, subscribe a browser API (resize, online/offline, WebSocket), animazioni con cleanup, third-party library setup.

**Risorsa**: https://react.dev/learn/you-might-not-need-an-effect — "the best documentation article I've ever read" (Neciu Dan)

---

## Tip 5 — Stop using index as key {#tip-5}

**Rule**: usa un ID stabile e unico dai tuoi dati come `key`. `key={index}` è corretto solo per liste puramente display (senza state nei children).

**Why it matters**: React usa `key` per mappare il virtual DOM al DOM reale. Con `key={index}`, quando rimuovi il primo item, React vede "la lista si è accorciata di 1" e mantiene i DOM node esistenti spostando i dati — l'input al DOM node 0 conserva il testo digitato dall'utente, che ora appare affiancato al secondo item. React non ha rimosso il DOM node giusto.

**Bad**
```jsx
// ❌ text digitato in un input "salta" di riga quando un item precedente viene rimosso
{items.map((item, i) => (
  <li key={i}>
    {item.text} <input placeholder="Type something..." />
  </li>
))}
```

**Good**
```jsx
// ✅ React rimuove esattamente il DOM node corretto
{items.map((item) => (
  <li key={item.id}>
    {item.text} <input placeholder="Type something..." />
  </li>
))}
```

**Edge cases / quando key={index} è accettabile**
- Lista statica o append-only dove l'ordine non cambia mai.
- Children puramente display (nessun `useState`, nessun input, nessun form) — il riciclo dei DOM node non ha effetti visibili.
- In entrambi i casi, se arrivano ID dai dati, usarli è sempre preferibile.

**Se i dati non hanno ID**: è un problema di data modeling da correggere upstream (API o state). In emergenza: `crypto.randomUUID()` alla creazione dell'item (non durante il render).

---

## Tip 6 — key prop resets everything {#tip-6}

**Rule**: cambiare la `key` di un componente lo fa unmontare completamente e rimontare da zero — state azzerato, query ripartite. Usa questa meccanica invece di `useEffect` per gestire il reset di state legato a prop esterne.

**Why it matters**: un `useEffect` che osserva una prop per resettare state produce un render intermedio con lo state "vecchio" (il render con il nuovo userId ha ancora il form dello user precedente per un frame). Si desincronizza facilmente se si aggiunge nuovo state. La key solution è atomica e non richiede manutenzione.

**Bad**
```jsx
function UserSettingsForm({ userId }) {
  const [name, setName] = useState('');

  // ❌ fragile: devo ricordarmi di resettare ogni pezzo di state
  useEffect(() => {
    setName(''); // e se aggiungo altri useState, devo aggiornarli tutti qui
  }, [userId]);

  return <input value={name} onChange={e => setName(e.target.value)} />;
}
```

**Good**
```jsx
// ✅ key change = unmount + fresh mount: ogni state resettato automaticamente
<UserSettingsForm key={userId} userId={userId} />

function UserSettingsForm({ userId }) {
  const [name, setName] = useState('');
  // nessun useEffect di reset — non serve
  return <input value={name} onChange={e => setName(e.target.value)} />;
}
```

**Edge cases**
- Attenzione alle performance: unmount + mount esegue cleanup effect + setup effect nuovamente. Su componenti con animazioni di mount costose, considerare se vale la pena.
- La key solution si usa su qualsiasi componente (non solo liste) — è una funzionalità generale di React.

---

## Tip 7 — Il tuo useMemo è overhead {#tip-7}

**Rule**: profila prima di memoizzare. `useMemo`/`useCallback` non sono gratuiti — ad ogni render React esegue il hook, shallow-compara ogni dipendenza, e decide se restituire il valore cached o ricalcolare. Su computazioni triviali, questo overhead supera il risparmio.

**Why it matters**: memoizzare string concatenation o arithmetic è controproducente. Peggio ancora su React 19 con React Compiler attivo: il compiler inserisce automaticamente `useMemo`/`useCallback` dove servono — la memoizzazione manuale può interferire con le sue ottimizzazioni.

**Bad**
```jsx
// ❌ l'hook overhead > string concatenation
const fullName = useMemo(
  () => `${user.firstName} ${user.lastName}`,
  [user.firstName, user.lastName]
);

// ❌ idem per boolean
const isValid = useMemo(() => items.length > 0, [items]);
```

**Good**
```jsx
// ✅ calcolo diretto — nessun overhead
const fullName = `${user.firstName} ${user.lastName}`;
const isValid = items.length > 0;

// ✅ useMemo giustificato: computazione costosa su dataset grande
const sortedItems = useMemo(
  () => [...items].sort(complexCompareFn),
  [items]
);
```

**Context adjustments — React Compiler**
- Se `react >= 19.0.0` AND `babel-plugin-react-compiler` / `vite-plugin-react-compiler` nel progetto: la memoizzazione manuale diventa rumore e può interferire col compilatore → scala la severity da 🟢 Low a 🟡 Medium e suggerisci la rimozione.
- Se React < 19 o compiler non presente: consiglio "profila prima di memoizzare", non rimuovere incondizionatamente.

**Regola pratica**: memoizza solo se puoi dimostrare (con React DevTools Profiler) che il costo del ricalcolo è visibile. Per callback stabilizzare: `useCallback` è utile per evitare che figli con `React.memo` si re-renderizzino per reference instability.

---

## Tip 8 — SRP significa "one reason to change" {#tip-8}

**Rule**: Single Responsibility Principle = un componente dovrebbe avere una sola ragione per cambiare. Un componente che fa fetch + loading + error + rendering ne ha quattro.

**Why it matters**: quattro persone diverse del team editano lo stesso file per quattro motivi non correlati — API contract change, loading UX change, error handling change, card layout change. Ogni merge è un potenziale conflitto. Estrarre la data logic in un custom hook isola queste responsabilità.

**Bad**
```jsx
// ❌ UserProfile ha 4 ragioni per cambiare
const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => { setUser(data); setIsLoading(false); })
      .catch(() => { setError('Error'); setIsLoading(false); });
  }, [userId]);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  return <h1>Welcome, {user.name}</h1>;
};
```

**Good**
```jsx
// ✅ hook cambia solo se l'API cambia; componente cambia solo se il layout cambia
const useUserData = (userId) => {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });
  return { user, isLoading, error };
};

const UserProfile = ({ userId }) => {
  const { user, isLoading, error } = useUserData(userId);
  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Something went wrong!</p>;
  return <h1>Welcome, {user.name}</h1>;
};
```

**Edge cases**
- Non every-useState-extraction è SRP. Estrai solo quando ci sono davvero responsabilità ortogonali che cambiano per ragioni diverse.
- Questo è un `SUGGEST ONLY` — prima di proporre un nuovo custom hook, cerca se esiste già un hook simile in `src/hooks/`.

---

## Tip 9 — useLayoutEffect elimina il flicker {#tip-9}

**Rule**: usa `useLayoutEffect` quando misuri il DOM e modifichi immediatamente uno stile/posizione. Usa `useEffect` per tutto il resto. La differenza: `useLayoutEffect` corre dopo il DOM update ma *prima* del paint; `useEffect` corre dopo il paint.

**Why it matters**: con `useEffect`, il browser mostra il componente nel posto sbagliato per un frame (es. tooltip a `top: 0`), poi l'effect sposta al posto giusto — flicker visibile. Con `useLayoutEffect` l'utente non vede mai la posizione sbagliata.

**Bad — flicker**
```jsx
useEffect(() => {
  if (buttonRef.current && tooltipRef.current) {
    const { bottom } = buttonRef.current.getBoundingClientRect();
    tooltipRef.current.style.top = `${bottom + 10}px`;
    // ❌ il tooltip appare a top:0 per un frame, poi salta qui
  }
}, []);
```

**Good — no flicker**
```jsx
useLayoutEffect(() => {
  if (buttonRef.current && tooltipRef.current) {
    const { bottom } = buttonRef.current.getBoundingClientRect();
    tooltipRef.current.style.top = `${bottom + 10}px`;
    // ✅ posizione corretta dal primo frame
  }
}, []);
```

**Edge cases / quando NON usare useLayoutEffect**
- `useLayoutEffect` **blocca il paint** — se la logica è lenta, blocca il browser fino al completamento. Usalo solo per misurazioni DOM + stile.
- Se usi `useLayoutEffect` senza `getBoundingClientRect` o simili misurazione DOM → probabilmente basta `useEffect`.
- In SSR (Next.js Pages Router), `useLayoutEffect` genera un warning lato server — usa `useEffect` in quel contesto, o una guard `typeof window !== 'undefined'`.

---

## Tip 10 — Compound Components vs prop soup {#tip-10}

**Rule**: quando un'API componente accumula render props e flag di configurazione, usa il pattern Compound Components: parent + sub-component che comunicano via Context. Ogni Item gestisce il proprio stato con il proprio Context provider.

**Why it matters**: `<Accordion items={items} renderHeader={...} renderBody={...} onToggle={...} />` regge finché qualcuno non ha bisogno di un'icona custom solo nel terzo header. A quel punto l'API di render props collassa e devi riscrivere tutto. Con Compound Components, il markup è già composable.

**Bad — prop soup**
```jsx
<Accordion
  items={items}
  renderHeader={(item) => <span>{item.title}</span>}
  renderBody={(item) => <p>{item.content}</p>}
  onToggle={(index) => track(index)}
/>
```

**Good — Compound Components**
```jsx
import { createContext, useContext, useState } from 'react';

const AccordionItemContext = createContext(null);

function Accordion({ children }) {
  return <div className="accordion">{children}</div>;
}

function Item({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <AccordionItemContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="accordion-item">{children}</div>
    </AccordionItemContext.Provider>
  );
}

function Header({ children }) {
  const { setIsOpen } = useContext(AccordionItemContext);
  return <div onClick={() => setIsOpen(o => !o)}>{children}</div>;
}

function Body({ children }) {
  const { isOpen } = useContext(AccordionItemContext);
  return isOpen ? <div>{children}</div> : null;
}

Accordion.Item = Item;
Accordion.Header = Header;
Accordion.Body = Body;
```

**Utilizzo**
```jsx
<Accordion>
  <Accordion.Item>
    <Accordion.Header>
      Is this flexible? <CustomIcon /> {/* nessun problema */}
    </Accordion.Header>
    <Accordion.Body>You can put whatever you want here.</Accordion.Body>
  </Accordion.Item>
</Accordion>
```

**Edge cases**
- Il pattern funziona perché ogni `Item` crea il proprio Context provider — `Header` e `Body` trovano sempre il loro `Item` più vicino nell'albero, non un ancestor lontano.
- Questo è un `SUGGEST ONLY` — è un cambio di API pubblico che richiede aggiornamento di tutti i consumer.
- Per componenti con un solo "slot" di customizzazione, `children` prop è spesso sufficiente e più semplice.

---

## Trasversali fondamentali {#trasversali}

Pattern non nei 10 tip ma che violano direttamente la documentazione ufficiale React — nessuna opinione, solo errori.

### Rules of Hooks

**Rule**: i hook devono essere chiamati sempre nello stesso ordine, sempre al top level di un component/hook. Mai dentro `if`, `for`, funzioni nested, callback.

**Why it matters**: React internamente tiene una linked list delle chiamate hook nell'ordine in cui vengono chiamate ad ogni render. Se l'ordine cambia (es. `if (x) useState()` viene saltato), React associa hook sbagliati ai valori precedenti → crash o comportamento indeterminato.

**Bad**
```jsx
function Component({ isLoggedIn }) {
  if (isLoggedIn) {
    const [name, setName] = useState(''); // ❌ hook condizionale
  }
  useEffect(() => { ... }); // questo è ora il "primo" hook se isLoggedIn=false
}
```

**Good**
```jsx
function Component({ isLoggedIn }) {
  const [name, setName] = useState(''); // ✅ sempre chiamato
  // usa isLoggedIn dentro il component, non come guard
}
```

### Mutazione diretta dello state

**Rule**: non mutare mai un oggetto/array di state direttamente. Crea sempre una nuova reference.

**Why it matters**: React usa shallow equality per decidere se re-renderizzare. Se muti l'oggetto esistente e lo ripassi al setter, React vede `prevState === newState` e non re-renderizza. Bug silenzioso.

**Bad**
```jsx
const [items, setItems] = useState([1, 2, 3]);

// ❌ tutti e tre mutano la reference esistente
items.push(4); setItems(items);
items[0] = 99; setItems(items);
items.sort(); setItems(items);
```

**Good**
```jsx
setItems([...items, 4]);          // ✅ spread
setItems(items.map((v, i) => i === 0 ? 99 : v));  // ✅ map
setItems([...items].sort());      // ✅ copia poi sort
```

### async useEffect

**Rule**: non passare una funzione `async` direttamente come primo argomento di `useEffect`. `useEffect` si aspetta che la funzione ritorni `undefined` o una cleanup function — una `async` function ritorna sempre una Promise.

**Why it matters**: il cleanup (return value) viene ignorato, quindi non puoi fare cancellazione. In aggiunta, in alcuni ambienti React emette un warning.

**Bad**
```jsx
useEffect(async () => {
  const data = await fetch('/api/data').then(r => r.json());
  setData(data); // ❌ cleanup impossibile
}, []);
```

**Good**
```jsx
useEffect(() => {
  let cancelled = false;
  async function load() {
    const data = await fetch('/api/data').then(r => r.json());
    if (!cancelled) setData(data);
  }
  load();
  return () => { cancelled = true; }; // ✅ cleanup funziona
}, []);
```

### Functional updates per setState

**Rule**: quando il nuovo valore di state dipende dal valore precedente inside a callback o timer, usa la forma funzionale del setter: `setState(prev => nextValue)`.

**Why it matters**: le closure catturano il valore di state al momento della loro creazione. In un `setInterval` con deps array vuota, `count` è sempre `0` — stale closure. La forma funzionale legge sempre il valore attuale dallo state interno di React, non dalla closure.

**Bad**
```jsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + 1); // ❌ count è stale (sempre 0)
  }, 1000);
  return () => clearInterval(id);
}, []); // count non è in deps → closure stale
```

**Good**
```jsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1); // ✅ legge il valore attuale
  }, 1000);
  return () => clearInterval(id);
}, []); // nessuna dipendenza necessaria
```

**Quando applicare**: segnala solo se il setter usa una variabile di state come operando dentro callback/timer/listener con una deps array che non include quella variabile (possibile stale closure).
