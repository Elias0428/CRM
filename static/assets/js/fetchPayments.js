function listenAllCheckInput() {
    let paymentsTable = document.getElementById('paymentsTable')
    let checkboxes = paymentsTable.querySelectorAll('input[type="checkbox"]');

    let actionRequiredTable = document.getElementById('actionRequiredTable')
    let checkboxesActionRequired = actionRequiredTable.querySelectorAll('input[type="checkbox"]');

    // Para cada checkbox, agregar un oyente de eventos que se dispare al cambiar el estado del checkbox
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {            
            toggleUserStatus(checkbox)
        });
    });

    checkboxesActionRequired.forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {            
            toogleActionRequired(checkbox)
        });
    });
}

function toggleUserStatus(checkbox) {
    const formData = new FormData();
    formData.append('obamaCare', obamacare_id);
    formData.append('month', checkbox.value);

    if (checkbox.checked) {

        fetch(`/fetchPaymentsMonth/`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())  // Procesar la respuesta (si es JSON)
        .then(data => {
            //console.log(data.success)
            if (data.success){
                //console.log("User role:", data.role); // Debugging
                if (data.success && data.role != "Admin") {
                    checkbox.disabled = true;
                }
            }
        })
        .catch(error => console.error('Error:', error));  // Manejo de errores
    } else {
        // Si se desmarca el checkbox, eliminar el pago
        fetch(`/fetchPaymentsMonth/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                obamaCare: obamacare_id,
                month: checkbox.value
            })
        })
        .then(response => response.json())  
        .then(data => {
            if (data.success) {
                console.log("Payment deleted successfully");
            } else {
                console.error("Error deleting payment:", data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// fetch para Action Required
function toogleActionRequired(checkbox) {
    const formData = new FormData();
    formData.append('obama', obamacare_id); // Asegúrate de que obamacare_id esté definido

    console.log(obamacare_id,'********')

    fetch('/fetchActionRequired/', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data, '************');
        if (data && data.success) { // Verifica si data y data.success existen
            console.log('User role:', data.role);
            checkbox.disabled = true;
        } else {
          console.error("Error en la respuesta del servidor:", data)
          alert("Ocurrio un error al procesar la solicitud.")
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Ocurrio un error de red o en el servidor.");
    });
}

document.addEventListener('DOMContentLoaded', listenAllCheckInput);