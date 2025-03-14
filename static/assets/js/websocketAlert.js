document.addEventListener("DOMContentLoaded", function () {
    const userRole = document.body.getAttribute("data-user-role");
    const userId = document.body.getAttribute("data-user-id");

    if (!userRole || !userId) return;  // Si no hay usuario, no hace nada

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

    // WebSocket para alertas generales
    const socketGeneral = new WebSocket(protocol + window.location.host + "/ws/alerts/");

    socketGeneral.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.event_type === "new_client" && !(userRole === "A" || userRole === "AU")) {
            Swal.fire({
                title: "New Client!",
                text: data.message,
                icon: "success",
                confirmButtonText: "Aceptar",
                timer: 5000
            });
        }
    };

    // WebSocket para alertas específicas del usuario
    const socketUser = new WebSocket(protocol + window.location.host + `/ws/alerts/user_alerts_${userId}/`);

    socketUser.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.event_type === "new_accion_required") {
            Swal.fire({
                title: "Action Required!",
                text: data.message,
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#19e207",
                cancelButtonColor: "#ea0907",
                confirmButtonText: "Go to customer with required action.",
                cancelButtonText: "Ignore"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.open(data.extra_info, "_blank");
                }
            });
        }

        if (data.event_type === "action_completed") {
            Swal.fire({
                title: "Action Completed!",
                text: data.message,
                icon: "info",
                confirmButtonText: "OK",
                timer: 5000
            });
        }
    };


});
