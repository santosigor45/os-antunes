document.addEventListener('DOMContentLoaded', function () {
    atualizarData();
    adminLoader();
    highlightActiveNavbarItem();
    exibirModal();
    exibirMensagemPersonalizada();
    setupFormListeners();
    setupPlacaInput();
    setupMotoristaInput();
    verificarPlaca()
});

// Add focus event listeners to all input fields to ensure they scroll into view.
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('focus', scrollToView);
});

const enviarBtn = document.getElementById('enviar-btn');
const camposDoFormulario = document.querySelectorAll('input, select');

// Disable the send button shortly after click to prevent multiple submissions.
if (enviarBtn) {
    enviarBtn.addEventListener('click', function () {
        setTimeout(function () {
            enviarBtn.disabled = true;
        }, 100);
    });

    camposDoFormulario.forEach(function (campo) {
        campo.addEventListener('input', function () {
            enviarBtn.disabled = false;
        });
    });
}

// Modify admin-specific links if the user is an administrator.
function adminLoader() {
    var userContainer = document.getElementById('username-link')
    if (typeof isAdmin !== 'undefined' && isAdmin) {
        if (isAdmin === true) {
            userContainer.setAttribute('href', "/admin")

        }
    }
}

// Check server availability.
function checkServerAvailability() {
    return fetch('/ping')
        .then(response => response.ok ? true : false)
        .catch(() => false);
}

// Scroll the active element smoothly into view after a delay.
function scrollToView(event) {
    var activeElement = event.target;
    setTimeout(() => {
        activeElement.scrollIntoView({behavior: 'smooth', block: 'center'});
    }, 300);
}

// Set up event listeners for forms to handle submissions and interact with the server.
function setupFormListeners() {
    document.querySelectorAll('form.dados').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            var formData = new FormData(this);
            var formId = form.getAttribute('id');
            var url = '/process_form/send';

            // Envia o formulário e lida com a resposta como HTML
            fetch(url, {
                method: form.getAttribute('method'),
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao processar o formulário.');
                }
                return response.json();
            })
            .then(data => {
                if (data.type === 'success') {
                    // Limpar o formulário e exibir mensagens de sucesso
                    limparFormulario(formId);
                    showHiddenDiv(['container-fornecedor'], ['add']);
                    exibirMensagemFlash(data.message, 'success');

                    // Abrir uma nova janela e inserir o HTML retornado
                    const printWindow = window.open('', '_blank');

                    if (printWindow) {
                        printWindow.document.open();
                        printWindow.document.write(data.html);
                        printWindow.document.close();

                        // Aguarda o conteúdo carregar antes de imprimir
                        printWindow.onload = function() {
                            printWindow.focus();
                            printWindow.print();

                            // Opcional: Fechar a janela após a impressão
                            printWindow.onafterprint = function() {
                                printWindow.close();
                            };
                        };
                    } else {
                        exibirMensagemFlash('Não foi possível abrir a janela de impressão.', 'error');
                    }
                } else {
                    // Exibir mensagem de erro
                    exibirMensagemFlash(data.message, 'error');
                }
            })
            .catch(error => {
                exibirMensagemFlash('Houve um erro. Por favor, tente novamente.', 'info');
                console.error(error);
            });
        });
    });
}

// Convert FormData into a simple object.
function formDataToObject(formData) {
    var formDataObject = {};
    formData.forEach(function(value, key){
        formDataObject[key] = value;
    });
    return formDataObject;
}

// Send form data to server and handle the response.
function sendDataToServer(url, formData, method) {
    if (method == 'GET') {
        return fetch(url, { method: method}).then(response => response.json());
    } else {
        return fetch(url, { method: method, body: formData }).then(response => response.json());
    };
}

// Validates and formats the vehicle plate input.
function verificarPlaca() {
    var placaElement = document.getElementById("placa");
    var kmElement = document.getElementById("quilometragem");
    if (placaElement.value == "SEM-PLACA") {
        placaElement.removeAttribute('pattern');
        placaElement.maxLength = "9"
        kmElement.required = false;
        document.getElementById("div-descricao").style.display = "block";
        document.getElementById("descricao").required = true;
    } else {
        placaElement.pattern = "[A-Z]{3}-\\d[A-j0-9]\\d{2}"
        placaElement.maxLength = "8"
        kmElement.required = true;
        document.getElementById("div-descricao").style.display = "none";
        document.getElementById("descricao").required = false;
    }
}

function setupPlacaInput(field = 'placa') {
    var placa = document.getElementById(field);

    placa.addEventListener('input', function() {
        placa.value = placa.value.toUpperCase();
        setupPlacaPattern(field);
    });

    setupPlacaOptions(field);
}

function setupPlacaOptions(field) {
    var placaOptions = document.getElementById('placaOptions');

    if (!placaOptions) {
        return
    }

    var placa = document.getElementById(field);
    var all_placas = Array.from(placaOptions.children);

    placa.addEventListener('input', function() {
        var valorAtual = placa.value;
        placaOptions.innerHTML = '';

        filterAndDisplayOptions(valorAtual, all_placas, placa, placaOptions);
    });

    placa.addEventListener('blur', function() {
        setTimeout(function() {
            placaOptions.classList.remove('show');
        }, 300);
    });
}

function setupMotoristaInput() {
    var motorista = document.getElementById('motorista');
    var motoristaOptions = document.getElementById('motoristaOptions');

    if (!motoristaOptions) {
        return
    }

    var all_motoristas = Array.from(motoristaOptions.children);

    motorista.addEventListener('input', function() {
        motorista.value = motorista.value.toUpperCase().replace(/[0-9]/g, '');
        var valorAtual = motorista.value;
        motoristaOptions.innerHTML = '';

        filterAndDisplayOptions(valorAtual, all_motoristas, motorista, motoristaOptions);
    });

    motorista.addEventListener('blur', function() {
        setTimeout(function() {
            motoristaOptions.classList.remove('show');
        }, 300);
    });
}

// setup the field "Placa" to correspond to a specific pattern
function setupPlacaPattern(field) {
    var placa = document.getElementById(field);
    var valorAtual = placa.value;

    if (valorAtual.length <= 3) {
        placa.value = valorAtual.replace(/[^A-Z]/g, '');
    }
    else if (valorAtual.length === 4 && valorAtual.charAt(3) !== '-' && valorAtual.charAt(3) >= '0' && valorAtual.charAt(3) <= '9') {
        placa.value = valorAtual.substring(0, 3) + '-' + valorAtual.charAt(3);
    }
    else if (valorAtual.length === 6) {
        placa.value = valorAtual.substring(0, 5) + valorAtual.charAt(5).replace(/[^A-J0-9]/g, '');
    }
    else if (valorAtual.length >= 7) {
        placa.value = valorAtual.substring(0, 6) + valorAtual.charAt(6).replace(/[^0-9]/g, '') + valorAtual.charAt(7).replace(/[^0-9]/g, '');
    }
    else if (valorAtual.length === 4) {
        placa.value = valorAtual.slice(0, -1);
    }

    placa.addEventListener('keydown', function(event) {
        var valorAtual = placa.value;

        if (event.key === 'Backspace') {
            if (valorAtual.length === 5) {
                placa.value = valorAtual.slice(0, -1);
            }
        }
    });
}

function setupOnlyLetters(idElement) {
    element = document.getElementById(idElement);
    element.value = element.value.toUpperCase().replace(/[0-9]/g, '');
}

// filters and organize dynamic options based on the user input
function filterAndDisplayOptions(valorAtual, allOptions, inputField, optionsContainer) {
    optionsContainer.innerHTML = '';

    if (valorAtual.length === 0) {
        optionsContainer.classList.remove('show');
        return;
    }

    const valorAtualUpper = valorAtual.toUpperCase();
    let matches = [];

    for (const option of allOptions) {
        const optionValue = option.innerText.toUpperCase();

        if (optionValue.includes(valorAtualUpper)) {
            const index = optionValue.indexOf(valorAtualUpper);
            matches.push({option, index});
        }
    }

    matches.sort((a, b) => a.index - b.index);

    for (const match of matches) {
        const clonedOption = match.option.cloneNode(true);
        optionsContainer.appendChild(clonedOption);

        clonedOption.addEventListener('click', function() {
            inputField.value = clonedOption.innerText.split(' |')[0];
            optionsContainer.classList.remove('show');
        });
    }

    optionsContainer.classList.add('show');
}

// Confirm the intention to clear the form data with a confirmation dialog.
function confirmarLimpeza(form) {
    var confirmar = confirm("Tem certeza que deseja limpar tudo?");
    if (confirmar) {
        limparFormulario(form);
    }
}

// Resets the form fields and updates the date to the current date.
function limparFormulario(form) {
    var formulario = document.getElementById(form);
    formulario.reset();
    atualizarData();
}

// Validates and formats the vehicle plate input.
function verificarPlaca() {
    var placaElement = document.getElementById("placa");
    var descricaoDiv = document.getElementById("div-descricao");
    var descricaoElement = document.getElementById("descricao");

    if (placaElement.value == "SEM-PLACA") {
        placaElement.removeAttribute('pattern');
        placaElement.maxLength = "9";
        descricaoDiv.classList.remove('hidden')
        descricaoElement.required = true;
    } else {
        placaElement.pattern = "[A-Z]{3}-\\d[A-j0-9]\\d{2}"
        placaElement.maxLength = "8"
        descricaoDiv.classList.add('hidden')
        descricaoElement.required = false;
    }
}

// Highlights the navbar item that corresponds to the current page URL.
function highlightActiveNavbarItem() {
    let currentUrl = window.location.href;
    let navbarItems = document.querySelectorAll(".navbar-nav .nav-link");
    navbarItems.forEach((navbarItem) => {
        if (currentUrl.includes(navbarItem.href)) {
            navbarItem.classList.add("active");
        }
    })
}

// Updates the date/time input field to today's date in ISO format.
function atualizarData() {
    var today = new Date();
    var offset = today.getTimezoneOffset() * 60000;
    var localISOTime = (new Date(today - offset)).toISOString();

    dataElement = document.getElementById('data')
    timeElement = document.getElementById('hora')

    if (dataElement) {
        dataElement.value = localISOTime.split('T')[0];
        timeElement.value = localISOTime.split('T')[1].slice(0, -8);
    }
}

// Displays a personalized greeting based on the current time of day.
function exibirMensagemPersonalizada() {
    var agora = new Date();
    var hora = agora.getHours();
    var mensagem = hora < 12 ? "Bom dia, " : hora < 18 ? "Boa tarde, " : "Boa noite, ";
    var elementoMensagem = document.getElementById("welcome_message");
    if (elementoMensagem) {
        elementoMensagem.innerHTML = mensagem + elementoMensagem.innerHTML;
    }
}

// Displays and manages flash messages in a modal.
function exibirMensagemFlash(mensagem, tipo) {
    var modal = document.getElementById('jsModal');
    modal.classList.add('show');
    var flash_content = document.getElementById('js-flash-content');
    var flash_text = document.getElementById('js-flash-text');
    flash_text.classList.add("flash-text-" + tipo);
    flash_content.classList.add("flash-" + tipo);
    flash_text.innerHTML = mensagem;
    setTimeout(function () {
        flash_text.classList.remove("flash-text-" + tipo);
        flash_content.classList.remove("flash-" + tipo);
        fecharModal(modal.getAttribute("id"));
    }, 3000);
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            fecharModal(modal.getAttribute("id"));
        }
    });
}

// Displays a modal if there are any flash messages.
function exibirModal() {
    var modal = document.getElementById('myModal');
    var flashes = document.querySelector('.flashes');
    if (flashes && flashes.children.length > 0) {
        modal.classList.add('show');
        setTimeout(function () {
            fecharModal(odal.getAttribute("id"));;
        }, 3000);
        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                fecharModal(modal.getAttribute("id"));;
            }
        });
    }
}

// Closes the modal with a fade-out effect.
function fecharModal(modal_id) {
    var modal = document.getElementById(modal_id);
    modal.classList.add('fade-out');
    setTimeout(function () {
        modal.classList.remove('show', 'fade-out');
    }, 200);
}

// Control the appearing/disappearing style of any div
function showHiddenDiv(element, option) {
    var elementControlled = []
    for (var i = 0; i < element.length; i++) {
        elementControlled[i] = document.getElementById(element[i]);

        if (option.length <= 1) {
            if (option == 'add') {
                elementControlled[i].classList.add('hidden');
            } else if (option == 'remove') {
                elementControlled[i].classList.remove('hidden');
            }
        } else {
            if (option[i] == 'add') {
                elementControlled[i].classList.add('hidden');
            } else if (option[i] == 'remove') {
                elementControlled[i].classList.remove('hidden');
            }
        }
    }
}

function removeAddRequired(element, option) {
    var elementControlled = []
    for (var i = 0; i < element.length; i++) {
        elementControlled[i] = document.getElementById(element[i]);

        if (option.length <= 1) {
            if (option == 'add') {
                elementControlled[i].required = true;
            } else if (option == 'remove') {
                elementControlled[i].required = false;
            }
        } else {
            if (option[i] == 'add') {
                elementControlled[i].required = true;
            } else if (option[i] == 'remove') {
                elementControlled[i].required = false;
            }
        }
    }
}
