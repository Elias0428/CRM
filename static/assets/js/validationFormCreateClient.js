document.getElementById('buttonSend').addEventListener('click', sendPost);


function sendPost() {
    var formData = new FormData();
    formData.append('nameDependent', document.getElementById('nameDependent').value)
    formData.append('sexDependent', document.getElementById('sexDependent').value)
    formData.append('dateBirthDependent', document.getElementById('dateBirthDependent').value)
    formData.append('applyDependent', document.getElementById('applyDependent').value)
    formData.append('migrationStatusDependent', document.getElementById('migrationStatusDependent').value)
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)

    fetch(`/json/`, {
        method: "POST",
        body: formData,
    })
    .then((response) => response.json()) // Parsea la respuesta JSON
    .then((data) => {
        if (data.error) {
            console.error("Error:", data.error);
            // Manejar el error, por ejemplo, mostrar un mensaje de error al usuario
        } else {
            console.log("Mensaje de éxito:", data.sms);
            
            // Realizar acciones de éxito, si es necesario
        }
    })
    .catch((error) => {
        console.error("Error en la solicitud:", error);
        // Manejar errores en la solicitud, como problemas de red
    });
}