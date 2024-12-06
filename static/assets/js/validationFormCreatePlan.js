document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('buttonSendObama')?.addEventListener('click', saveAcaPlan);
    document.getElementById('buttonSendSupp')?.addEventListener('click', saveSupplementaryPlan);
    document.getElementById('buttonSendDepend')?.addEventListener('click', saveDependents);
});

var idAcaPlan

function saveAcaPlan() {

    var formData = new FormData();
    formData.append('type_sales', type_sales)
    formData.append('taxes', document.getElementById('taxes').value)
    formData.append('agent_usa', document.getElementById('agent_usa').value)
    formData.append('planName', document.getElementById('planName').value)
    formData.append('work', document.getElementById('work').value)
    formData.append('subsidy', document.getElementById('subsidy').value)
    formData.append('carrierObama', document.getElementById('carrierObama').value)
    formData.append('applyObama', document.getElementById('applyObama').value)
    formData.append('observationObama', document.getElementById('observationObama').value)
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)

    var acaPlanId = document.getElementById('acaPlanId').value;
    var acaPlan = document.getElementById('acaPlan').value;
    if (acaPlanId) {
        formData.append('acaPlanId', acaPlanId);
    }

  
    fetch(`/fetchAca/${client_id}/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Actualizar la interfaz de usuario según sea necesario
        stepper1.next();
        idAcaPlan = acaPlan
        //console.log(idAcaPlan)
        
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
      const agent_usa = plan.querySelector('[name="agent_usa"]').value;
      const premiumSupp = plan.querySelector('[name="premiumSupp"]').value;
      const policyTypeSupp = plan.querySelector('[name="policyTypeSupp"]').value;
      const preventiveSupp = plan.querySelector('[name="preventiveSupp"]').value;
      const coverageSupp = plan.querySelector('[name="coverageSupp"]').value;
      const deducibleSupp = plan.querySelector('[name="deducibleSupp"]').value;
      const observationSuple = plan.querySelector('[name="observationSuple"]').value;
      const suppIdField = plan.querySelector('[name="suppId"]');
      
      let suppId = suppIdField ? suppIdField.value : '';

      // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
      if (agent_usa.trim() !== '') {
          // Agregar cada dependiente al formData con un índice
          if (plan.querySelector('[name="suppId"]')){
            formData.append(`supplementary_plan_data[${index}][id]`, suppId);
          }          
          formData.append(`supplementary_plan_data[${index}][effectiveDateSupp]`, effectiveDateSupp);
          formData.append(`supplementary_plan_data[${index}][agent_usa]`, agent_usa);
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
  fetch(`/fetchSupp/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          //console.log('IDs actualizados:', data.supp_ids);
          plans.forEach((plan, index) => {
            suppIdInputHidden = plan.querySelector('[name="suppId"]')
            //console.log(suppIdInputHidden)
            if (suppIdInputHidden.value == ''){
              // si imput esta vacio se le coloca el id recivido del parte del bakend
              suppIdInputHidden.value = data.supp_ids[index]
            }
          });

          // Actualizar la interfaz de usuario según sea necesario
          stepper1.next();
          addTypesDependent()
      } else {
          // Manejar errores
          //console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
    //console.error('Error en la solicitud:', error);
  });
}
  
function saveDependents() {
  var formData = new FormData();
  formData.append('type_sales', 'DEPENDENTS');
  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

  //console.log('Formulario inicializado con CSRF:', document.querySelector('[name=csrfmiddlewaretoken]').value);  // Verificar CSRF

  // Recorrer todos los conjuntos de dependientes
  const dependents = document.querySelectorAll('.dependentClassList'); // Ajustado el selector aquí.
  dependents.forEach((dependent, index) => {
    //console.log(`Procesando dependiente ${index + 1}...`); // Verificar el índice del dependiente procesado

    // Obtener los valores de cada conjunto de dependientes
    const kinship = dependent.querySelector('[name="kinship"]').value;
    const nameDependent = dependent.querySelector('[name="nameDependent"]').value;
    const applyDependent = dependent.querySelector('[name="applyDependent"]').value;
    const dateBirthDependent = dependent.querySelector('[name="dateBirthDependent"]').value;
    const migrationStatusDependent = dependent.querySelector('[name="migrationStatusDependent"]').value;
    const sexDependent = dependent.querySelector('[name="sexDependent"]').value;


    // Ajuste aquí para obtener los valores seleccionados de un select múltiple
    const typePoliceField = dependent.querySelector('[name="typePoliceDependents[]"]');
    let typePolice = [];

    // Si el campo select existe, obtener los valores seleccionados
    if (typePoliceField) {
        // Obtener los valores seleccionados
        typePolice = Array.from(typePoliceField.selectedOptions)
            .map(option => option.value);
        
        // Mostrar los valores seleccionados en 'typePolice'
        //console.log('Valores seleccionados en typePolice:', typePolice);
    }

    // Aquí estamos manejando el 'dependentId' como lo hicimos antes
    const dependentIdField = dependent.querySelector('[name="dependentId"]');
    let dependentId = dependentIdField ? dependentIdField.value : '';

    // Mostrar el dependentId
    //console.log('Dependent ID:', dependentId);

    // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
    if (nameDependent.trim() !== '') {
        //console.log('Enviando dependiente al formData:', index + 1);

        // Agregar cada dependiente al formData con un índice
        if (dependentId) {
          formData.append(`dependent[${index}][id]`, dependentId);
        }
        formData.append(`dependent[${index}][kinship]`, kinship);
        formData.append(`dependent[${index}][nameDependent]`, nameDependent);
        formData.append(`dependent[${index}][applyDependent]`, applyDependent);
        formData.append(`dependent[${index}][dateBirthDependent]`, dateBirthDependent);
        formData.append(`dependent[${index}][migrationStatusDependent]`, migrationStatusDependent);
        formData.append(`dependent[${index}][sexDependent]`, sexDependent);
        
        // Si se han seleccionado opciones en 'typePolice', agregarlas
        if (typePolice.length > 0) {
          formData.append(`dependent[${index}][typePoliceDependents]`, typePolice);
          //console.log('Agregando typePolice al formData:', typePolice);  // Verificar qué valores de 'typePolice' se agregan
        }
    }
  });

  //console.log('FormData antes de la solicitud fetch:', formData);

  // Realizar la solicitud fetch
  fetch(`/fetchDependent/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      //console.log('Respuesta del servidor:', data);  // Verificar la respuesta del servidor

      if (data.success) {
          //console.log('IDs actualizados:', data.dependents_ids);
          //console.log('Éxito:', data.success);
          
          // Actualizar la interfaz de usuario según sea necesario
          stepper1.next();
          if (data.success) {
            Swal.fire({
              icon: 'success' ,
              title: '<p style="color: black;">Saved success</p>',
              confirmButtonText: "OK",
            }).then((result) => {
              /* Read more about isConfirmed, isDenied below */
              if (result.isConfirmed) {
                window.location.href = '/';
              }
            });
          }
      } else {
          // Manejar errores
          //console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
      //console.error('Error en la solicitud:', error);
  });
}

function addTypesDependent() {
  const policyTypeSuppSelect = document.querySelectorAll('select[name="policyTypeSupp"]');
  const typePoliceSelects = document.querySelectorAll('select[name="typePoliceDependents[]"]');

  // Verificar que se encuentren los selects necesarios
  if (policyTypeSuppSelect.length === 0 || typePoliceSelects.length === 0) {
    //console.error("No se encontraron los selects necesarios.");
    return;
  }

  // Agregar opciones dinámicamente dependiendo del select policyTypeSupp
  policyTypeSuppSelect.forEach(policySelect => {
    const selectedPolicyType = policySelect.value; // Obtener el valor seleccionado de policyTypeSupp

    if (selectedPolicyType) {
      typePoliceSelects.forEach(typePoliceSelect => {
        // Verificar si la opción ya existe en el select
        const optionExists = Array.from(typePoliceSelect.options).some(option => option.value === selectedPolicyType);
        if (!optionExists) {
          const newOption = document.createElement('option');
          newOption.value = selectedPolicyType;
          newOption.textContent = selectedPolicyType;
          typePoliceSelect.appendChild(newOption); // Añadir la opción al select
        }
      });
    }
  });

  // Verificar si idAcaPlan es "ACA" y agregar la opción "Elias" si es necesario
  if (idAcaPlan === "ACA") {
    typePoliceSelects.forEach(typePoliceSelect => {
      // Verificar si la opción 'Elias' ya existe
      const optionExists = Array.from(typePoliceSelect.options).some(option => option.value === "Elias");
      if (!optionExists) {
        const newOption = document.createElement('option');
        newOption.value = "ACA";  // Establecer el valor de la opción
        newOption.textContent = "ACA";  // Establecer el texto visible de la opción
        typePoliceSelect.appendChild(newOption); // Añadir la opción "Elias" al select
      }
    });
  }

  // Inicializar Choices.js solo si no tiene la clase 'choices__input'
  typePoliceSelects.forEach(select => {
    if (!select.classList.contains('choices__input')) {
      new Choices(select, {
        removeItemButton: true,
        searchEnabled: true,
        placeholder: true,
        placeholderValue: 'Select options',
      });
    }
  });
}






