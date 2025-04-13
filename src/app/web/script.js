let minDesktopResolution = 1000;

let isInit = false;
let isMobile = false;
let currency_value = null;
let arrows = null;
let switchCurrency = null;

document.addEventListener("DOMContentLoaded", initialization);
document.addEventListener("DOMContentLoaded", func);
window.addEventListener("resize", check_resolution);

function print(message)
{
    console.log(message);
}

function initialization()
{
    arrows = document.querySelector("div.flex-container.currency-value img.arrows");
    currency_value = document.querySelector("div.flex-container.currency-value");
    switchCurrency = document.querySelector("div.flex-container.currency img");
    isInit = true;
    setDesktop();
    check_resolution();
    print("Инициализация завершена!");
}

function check_resolution()
{
    if(!isInit) return;

    if(!isMobile && window.outerWidth < minDesktopResolution)
    {
        setMobile();
        print("Ставим мобильную версию...");
    }
    else if(isMobile && window.outerWidth >= minDesktopResolution)
    {
        setDesktop();
        print("Ставим десктопную версию...");
    }
}

function setMobile()
{
    isMobile = true;

    currency_value.style.flexFlow = "column";
    currency_value.parentElement.style.flexFlow = "row";

    arrows.src = "./icons/sync_alt.svg";
    arrows.className = "mobile-arrows";

    switchCurrency.parentElement.parentElement.style.flexFlow = "column";
}

function setDesktop()
{
    isMobile = false;

    currency_value.style.flexFlow = "row";
    currency_value.parentElement.style.flexFlow = "column";

    arrows.src = "./icons/arrows.svg";
    arrows.className = "arrows";

    switchCurrency.parentElement.parentElement.style.flexFlow = "row";
}

function func() {
    const elements = {
        fromSelect: document.getElementById('fromCurrency'),
        toSelect: document.getElementById('toCurrency'),
        form: document.getElementById('converterForm'),
        amountInput: document.getElementById('first-input'),
        result: document.getElementById('second-input'),
        list: document.getElementById('currency')
    };

    // Загрузка валют при старте
    loadCurrencies(elements.fromSelect, elements.toSelect);

    // Обработчик формы
    elements.form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleConversion(elements);
    });
}

function loadCurrencies(list) {
    fetch('/rates')
        .then(function(response) {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(function(currencies) {
            populateSelects(currencies, list);
        })
        .catch(function(error) {
            alert('Failed to load currencies');
        });
}

function handleConversion(elements) {
    const requestData = {
        from: elements.fromSelect.value,
        to: elements.toSelect.value,
        amount: elements.amountInput.value
    };

    fetch('/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(function(response) {
        if (!response.ok) throw new Error('Server error');
        return response.json();
    })
    .then(function(data) {
        if (data.error) throw new Error(data.error);
        elements.result.value = `${data.result}`;
    })
    .catch(function(error) {
        alert(error.message || 'Conversion failed');
    });
}

function populateSelects(currencies, list) {
     currencies.forEach(function(currency) {
            const option = document.createElement('option');
            option.value = currency.currency;
            list.appendChild(option);
        });
}

