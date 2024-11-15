document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('buttonSendObama')?.addEventListener('click', saveAcaPlan);
    document.getElementById('buttonSendSupp')?.addEventListener('click', saveSupplementaryPlan);
    document.getElementById('buttonSendDepend')?.addEventListener('click', saveDependents);
});


function saveAcaPlan() {

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

    var acaPlanId = document.getElementById('acaPlanId').value;
    if (acaPlanId) {
        formData.append('acaPlanId', acaPlanId);
    }

  
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
  var formData = new FormData();
  formData.append('type_sales', type_sales);
  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

  // Recorrer todos los conjuntos de dependientes
  const plans = document.querySelectorAll('.supplementaryClassList'); // Ajustado el selector aquí
  plans.forEach((plan, index) => {
    // Obtener los valores de cada conjunto de dependientes
      const effectiveDateSupp = plan.querySelector('[name="effectiveDateSupp"]').value;
      const carrierSuple = plan.querySelector('[name="carrierSuple"]').value;
      const premiumSupp = plan.querySelector('[name="premiumSupp"]').value;
      const policyTypeSupp = plan.querySelector('[name="policyTypeSupp"]').value;
      const preventiveSupp = plan.querySelector('[name="preventiveSupp"]').value;
      const coverageSupp = plan.querySelector('[name="coverageSupp"]').value;
      const deducibleSupp = plan.querySelector('[name="deducibleSupp"]').value;
      const observationSuple = plan.querySelector('[name="observationSuple"]').value;
      const suppIdField = plan.querySelector('[name="suppId"]');
      
      let suppId = suppIdField ? suppIdField.value : '';

      // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
      if (effectiveDateSupp.trim() !== '') {
          // Agregar cada dependiente al formData con un índice
          if (plan.querySelector('[name="suppId"]')){
            formData.append(`supplementary_plan_data[${index}][id]`, suppId);
          }          
          formData.append(`supplementary_plan_data[${index}][effectiveDateSupp]`, effectiveDateSupp);
          formData.append(`supplementary_plan_data[${index}][carrierSuple]`, carrierSuple);
          formData.append(`supplementary_plan_data[${index}][premiumSupp]`, premiumSupp);
          formData.append(`supplementary_plan_data[${index}][policyTypeSupp]`, policyTypeSupp);
          formData.append(`supplementary_plan_data[${index}][preventiveSupp]`, preventiveSupp);
          formData.append(`supplementary_plan_data[${index}][coverageSupp]`, coverageSupp);
          formData.append(`supplementary_plan_data[${index}][deducibleSupp]`, deducibleSupp);
          formData.append(`supplementary_plan_data[${index}][observationSuple]`, observationSuple);
      }
  });

  // Realizar la solicitud fetch
  fetch(`/formCreatePlan/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          console.log('IDs actualizados:', data.supp_ids);
          // Actualizar la interfaz de usuario según sea necesario
          stepper1.next();
      } else {
          // Manejar errores
          console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
    console.error('Error en la solicitud:', error);
  });
}
  
function saveDependents() {
  var formData = new FormData();
  formData.append('type_sales', 'DEPENDENTS');
  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

  // Recorrer todos los conjuntos de dependientes
  const dependents = document.querySelectorAll('.dependentClassList'); // Ajustado el selector aquí.
  dependents.forEach((dependent, index) => {
    // Obtener los valores de cada conjunto de dependientes
    // El if es para saber si manda un Id debe actualizar pero sino lo manda debe crear
    
    const kinship = dependent.querySelector('[name="kinship"]').value;
    const nameDependent = dependent.querySelector('[name="nameDependent"]').value;
    const applyDependent = dependent.querySelector('[name="applyDependent"]').value;
    const dateBirthDependent = dependent.querySelector('[name="dateBirthDependent"]').value;
    const migrationStatusDependent = dependent.querySelector('[name="migrationStatusDependent"]').value;
    const sexDependent = dependent.querySelector('[name="sexDependent"]').value;
    const typePolice = dependent.querySelector('[name="typePolice"]').value;
    const dependentIdField = dependent.querySelector('[name="dependentId"]');
      
    let dependentId = dependentIdField ? dependentIdField.value : '';

    // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
    if (nameDependent.trim() !== '') {
        // Agregar cada dependiente al formData con un índice
        if (dependent.querySelector('[name="dependentId"]')){
          formData.append(`dependent[${index}][id]`, dependentId);
        }
        formData.append(`dependent[${index}][kinship]`, kinship);
        formData.append(`dependent[${index}][nameDependent]`, nameDependent);
        formData.append(`dependent[${index}][applyDependent]`, applyDependent);
        formData.append(`dependent[${index}][dateBirthDependent]`, dateBirthDependent);
        formData.append(`dependent[${index}][migrationStatusDependent]`, migrationStatusDependent);
        formData.append(`dependent[${index}][sexDependent]`, sexDependent);
        formData.append(`dependent[${index}][typePolice]`, typePolice);
    }
  });
      

  // Realizar la solicitud fetch
  fetch(`/formCreatePlan/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          console.log('IDs actualizados:', data.dependents_ids);
          // Actualizar la interfaz de usuario según sea necesario
          window.location.href = '/index/'
          stepper1.next();
      } else {
          // Manejar errores
          console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
      console.error('Error en la solicitud:', error);
  });
}
