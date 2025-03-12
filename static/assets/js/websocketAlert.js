document.addEventListener("DOMContentLoaded", function () {
    const userRole = document.body.getAttribute("data-user-role");

    if (!userRole) return;

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const socket = new WebSocket(protocol + window.location.host + "/ws/alerts/");

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.event_type === 'new_client' && !(userRole === "A" || userRole === "AU")) {
            
            Swal.fire({
                title: "New Client!",
                text: data.message,
                icon: "success",
                confirmButtonText: "Aceptar",
                timer: 5000
            });

        }

        if ( userRole === "Admin" && data.event_type === 'new_accion_required' ) {

            
            Swal.fire({
                title: "Action Required!",
                text: data.message,
                icon: "warning",
                showCancelButton: "OK",
                confirmButtonColor: "#19e207",
                cancelButtonColor: "#ea0907",
                confirmButtonText: "Go to customer with required action.", // Cambiamos el texto del botón
                cancelButtonText:"Ignore"
            }).then((result) => {
                if (result.isConfirmed) {
                window.open(data.extra_info, '_blank'); // Abre la URL en una nueva pestaña
                }
            });             


        }
    };
});
