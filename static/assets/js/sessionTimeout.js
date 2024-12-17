// Función para manejar el cierre de sesión
function setupSessionTimeout() {
    console.log('🕒 Inicializando timeout de sesión');
    
    // Configuraciones de tiempo
    const TIMEOUT_DURATION = 4 * 60 * 1000; // 15 minutos
    const WARNING_TIME = 2 * 60 * 1000; // 2 minutos antes del cierre
    const AUTO_LOGOUT_AFTER_WARNING = 1 * 60 * 1000; // 1 minuto después de la alerta

    let timeoutId;
    let warningTimeoutId;
    let autoLogoutTimeoutId;

    // Función para cerrar sesión
    function performLogout() {
        console.log('🚪 Intentando cerrar sesión desde performLogout');
        
        try {
            fetch('/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('📡 Respuesta de logout:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('🔀 Datos de logout:', data);
                
                // Asegurarse de redirigir
                if (data.redirect_url) {
                    console.log(`🚦 Redirigiendo a: ${data.redirect_url}`);
                    window.location.href = data.redirect_url;
                } else {
                    console.log('🚦 Redirigiendo a login por defecto');
                    window.location.href = '/login/';
                }
            })
            .catch(error => {
                console.error('❌ Error en logout AJAX:', error);
                window.location.href = '/login/';
            });
        } catch (error) {
            console.error('❌ Error crítico en logout:', error);
            window.location.href = '/login/';
        }
    }

    // Función para mostrar advertencia
    function showWarning() {
        console.log('⚠️ Mostrando advertencia de cierre de sesión');
        
        // Mostrar confirmación
        const confirmed = confirm('Su sesión está a punto de expirar. Si no responde, se cerrará automáticamente en 1 minuto. ¿Desea continuar?');

        if (confirmed) {
            console.log('✅ Usuario confirmó advertencia, cerrando sesión.');
            performLogout(); // Cierra la sesión directamente si el usuario confirma
        } else {
            console.log('⏳ Usuario no respondió o canceló, preparando cierre automático');
            autoLogoutTimeoutId = setTimeout(() => {
                console.log('🕒 Tiempo de cierre automático alcanzado');
                performLogout();
            }, AUTO_LOGOUT_AFTER_WARNING);
        }
    }

    // Función para reiniciar temporizadores
    function resetTimer() {
        console.log('🔄 Reiniciando temporizadores');
        
        // Limpiar temporizadores anteriores
        clearTimeout(timeoutId);
        clearTimeout(warningTimeoutId);
        clearTimeout(autoLogoutTimeoutId);

        // Configurar nuevos temporizadores
        timeoutId = setTimeout(performLogout, TIMEOUT_DURATION);
        warningTimeoutId = setTimeout(showWarning, TIMEOUT_DURATION - WARNING_TIME);
        
        console.log(`⏰ Próxima advertencia en ${(TIMEOUT_DURATION - WARNING_TIME) / 1000} segundos`);
        console.log(`⏰ Cierre de sesión en ${TIMEOUT_DURATION / 1000} segundos`);
    }

    // Función para obtener cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Eventos para reiniciar el temporizador
    const resetEvents = [
        'mousedown', 
        'keydown', 
        'scroll', 
        'mousemove', 
        'touchstart'
    ];

    resetEvents.forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });

    // Iniciar temporizadores
    resetTimer();

    // Exportar función de logout manual si se necesita
    window.manualLogout = performLogout;
}

// Ejecutar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', setupSessionTimeout);
