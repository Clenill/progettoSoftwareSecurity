 async function logout(){
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST', 
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (err) {
            console.error("Errore nel caricamento dei medici:", err);
        }
    }