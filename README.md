# OmniText Backend

Questo progetto è un backend API sviluppato per dimostrare competenze avanzate in Python e Flask, utilizzando un approccio orientato agli oggetti (OOP) con pattern architetturali moderni.

## Tecnologie Utilizzate

### Flask
Flask è stato scelto come framework web principale per la sua leggerezza e flessibilità. Permette di costruire API RESTful in modo rapido mantenendo il controllo completo sulla struttura del progetto, senza imporre pattern rigidi come altri framework più pesanti.

### MongoDB con MongoEngine
Per la persistenza dei dati, ho scelto MongoDB per la sua flessibilità nello schema dei dati e per la sua scalabilità. MongoEngine è stato implementato come ODM (Object-Document Mapper) per fornire una astrazione orientata agli oggetti sopra MongoDB, facilitando la gestione dei modelli di dati in un contesto OOP.

### Flask-RESTX
Ho integrato Flask-RESTX per la documentazione automatica delle API tramite Swagger UI. Questo garantisce una documentazione sempre aggiornata e interattiva, migliorando notevolmente l'esperienza degli sviluppatori che utilizzano queste API.

### Pattern Architetturale
Il progetto implementa un pattern architetturale a livelli ben definiti:
- **Controller**: gestisce le richieste HTTP e le risposte
- **Service**: contiene la logica di business
- **Model**: rappresenta le entità di dominio e la persistenza
- **Contract**: definisce le interfacce per garantire l'aderenza ai principi SOLID

Questa separazione delle responsabilità dimostra una solida comprensione dei principi di progettazione del software e di OOP.

## Utilizzo delle API

### Swagger UI
Le API sono documentate e testabili direttamente tramite Swagger UI, accessibile all'indirizzo: 
http://localhost:5000/api/docs

### Postman
È possibile utilizzare Postman per interagire con le API. Di seguito alcuni esempi di endpoint disponibili:

- `GET /api/users/{user_id}`: Recupera un utente specifico
- `POST /api/users/create`: Crea un nuovo utente

## Dipendenze del Progetto

### Dipendenze Core
- **Flask**: Framework web per Python
- **MongoEngine**: ODM per MongoDB
- **Flask-RESTX**: Estensione per la documentazione API

### Dipendenze di Utility
- **python-dotenv**: Per la gestione delle variabili d'ambiente
- **bson**: Per la gestione degli ID MongoDB

### Dipendenze di Sviluppo
- **pytest**: Per i test unitari
- **flake8**: Per il linting del codice
- **black**: Per la formattazione del codice

Questo progetto dimostra una solida comprensione di Python, Flask, MongoDB e dei principi di progettazione orientata agli oggetti, implementando best practices moderne per lo sviluppo di APIs e del Backend.

## Test

Il progetto include test unitari completi che verificano la corretta funzionalità del layer di servizio.

### Test Implementati

I test si concentrano sui metodi della classe `UserService` e verificano:

- **Validazione Email**: Test per confermare che il validatore di email riconosca correttamente formati validi e invalidi
- **Recupero Utenti**: Test per il metodo `find_by_id` che verifica:
  - Recupero corretto di utenti esistenti
  - Gestione appropriata quando l'utente non esiste
- **Creazione Utenti**: Test per il metodo `create` che verifica:
  - Creazione corretta con dati validi
  - Validazione di input incompleti o invalidi
  - Gestione dei duplicati email
  - Gestione degli errori imprevisti

### Approccio ai Test

I test unitari utilizzano il pattern AAA (Arrange-Act-Assert) e sfruttano la libreria unittest.mock per simulare le dipendenze esterne, garantendo che i test siano:

- **Veloci**: Non richiedono connessioni a database reali
- **Isolati**: Ogni test è indipendente dagli altri
- **Ripetibili**: Producono sempre lo stesso risultato in qualsiasi ambiente
- **Auto-verificanti**: Determinano automaticamente se il test è passato o fallito

Questo approccio assicura che i cambiamenti al codice possano essere testati rapidamente e con fiducia.