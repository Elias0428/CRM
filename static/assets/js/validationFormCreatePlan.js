document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('buttonSendObama')?.addEventListener('click', saveAcaPlan);
    document.getElementById('buttonSendSupp')?.addEventListener('click', saveSupplementaryPlan);
    document.getElementById('buttonSendDepend')?.addEventListener('click', saveDependents);
});


function saveAcaPlan() {
    console.log(type_sales)

    var formData = new FormData();
    formData.append('type_sales', type_sales)
    formData.append('taxes', document.getElementById('taxes').value)
    formData.append('planName', document.getElementById('planName').value)
    formData.append('work', document.getElementById('work').value)
    formData.append('subsidy', document.getElementById('subsidy').value)
    formData.append('carrierObama', document.getElementById('carrierObama').value)
    formData.append('applyObama', document.getElementById('applyObama').value)
    formData.append('observationObama', document.getElementById('observationObama').value)
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)

  
    fetch(`/formCreatePlan/${client_id}/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Actualizar la interfaz de usuario según sea necesario
        stepper1.next();
      } else {
        // Manejar errores
      }
    })
    .catch(error => {
      // Manejar errores
    });
}
  
function saveSupplementaryPlan() {

    console.log(type_sales)

    var formData = new FormData();
    formData.append('type_sales', type_sales)
    formData.append('effectiveDate', document.getElementById('effectiveDate').value)
    formData.append('carrierSuple', document.getElementById('carrierSuple').value)
    formData.append('premium', document.getElementById('premium').value)
    formData.append('policyType', document.getElementById('policyType').value)
    formData.append('preventive', document.getElementById('preventive').value)
    formData.append('coverage', document.getElementById('coverage').value)
    formData.append('deducible', document.getElementById('deducible').value)
    formData.append('observationSuple', document.getElementById('observationSuple').value)
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)
  
    fetch(`/formCreatePlan/${client_id}/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Actualizar la interfaz de usuario según sea necesario
        stepper1.next();
      } else {
        // Manejar errores
      }
    })
    .catch(error => {
      // Manejar errores
    });
}
  
function saveDependents() {
    const form = document.getElementById('dependent-form');
    const formData = new FormData(form);
  
    fetch(`/formCreatePlan/${client_id}/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Actualizar la interfaz de usuario según sea necesario
        stepper1.next();
      } else {
        // Manejar errores
      }
    })
    .catch(error => {
      // Manejar errores
    });
}