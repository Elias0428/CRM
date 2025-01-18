const userSocket = new WebSocket('ws://' + window.location.host + '/ws/user-update/');
	
userSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.status === 'success') {
        Swal.fire({
            title: "<p class='text-dark'>Congratulations Jhonfer Mercado</p>",
            text: "Danny has sold a SUPP plan",
            icon: "success",
            confirmButtonText: "YeaH!",
        }).then((result) => {
            location.reload();
            if (result.isConfirmed) {
                location.reload();
            }
        });
        // Esperar 30 segundos (30000 milisegundos) antes de recargar la página
        setTimeout(function() {
            location.reload();  // Recarga la página
        }, 30000);  // 30 segundos
    }
};
