document.getElementById('formCreateClient').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el envío tradicional del formulario
        
        const formData = new FormData(this);

        fetch('/formCreateClient/', {
            method: "POST",
            body: formData,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                showModal('Error', data.error); // Muestra el error en el modal
            } else if (data.success) {
                showModal('Éxito', 'Cliente registrado correctamente', true, data.redirect_url);
            }
        })
        .catch((error) => {
            console.error("Error en la solicitud:", error);
            showModal('Error', 'Hubo un problema al procesar tu solicitud. Inténtalo de nuevo.');
        });
    });

    // Función para mostrar el modal con un título, mensaje y redirección opcional
    function showModal(title, message, redirect = false, redirectUrl = '') {
        document.getElementById('modalLabel').textContent = title;
        document.getElementById('modalMessage').textContent = message;
        
        // Inicializar el modal
        let modal = new bootstrap.Modal(document.getElementById('responseModal'));
        modal.show();
        
        // Evento para redirigir cuando se cierra el modal
        document.getElementById('responseModal').addEventListener('hidden.bs.modal', function () {
            if (redirect && redirectUrl) {
                window.location.href = redirectUrl;
            }
    });
}
