let minDesktopResolution = 1000;

let isInit = false;
let isMobile = false;
let currency_value = null;
let arrows = null;
let switchCurrency = null;

document.addEventListener("DOMContentLoaded", initialization);
document.addEventListener('DOMContentLoaded', initConverter);
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

    arrows.src = "/static/icons/sync_alt.svg";
    arrows.className = "mobile-arrows";

    switchCurrency.parentElement.parentElement.style.flexFlow = "column";
}

function setDesktop()
{
    isMobile = false;

    currency_value.style.flexFlow = "row";
    currency_value.parentElement.style.flexFlow = "column";

    arrows.src = "/static/icons/arrows.svg";
    arrows.className = "arrows";

    switchCurrency.parentElement.parentElement.style.flexFlow = "row";
}

function initConverter() {
    // Инициализация элементов
    const elements = getDOMElements();
    setupEventListeners(elements);
    loadCurrencies(elements.currencyDatalist);
}

function getDOMElements() {
    return {
        form: document.getElementById('converterForm'),
        fromInput: document.getElementById('fromCurrency'),
        toInput: document.getElementById('toCurrency'),
        firstValue: document.getElementById('first-input'),
        secondValue: document.getElementById('second-input'),
        swapBtn: document.querySelector('.currency button'),
        currencyDatalist: document.getElementById('currency')
    };
}

function setupEventListeners(elements) {
    // Основные обработчики событий
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.swapBtn.addEventListener('click', handleSwapCurrencies);

    // Автообновление при вводе
    const inputs = [elements.firstValue, elements.secondValue, elements.fromInput, elements.toInput];
    inputs.forEach(input => {
        input.addEventListener('input', debounce(() => convertValues(elements), 300));
    });
}

async function loadCurrencies(datalist) {
    try {
        const response = await fetch('/rates');
        const currencies = await response.json();
        populateCurrencyList(currencies, datalist);
    } catch (error) {
        showError('Не удалось загрузить список валют');
    }
}

function populateCurrencyList(currencies, datalist) {
    currencies.forEach(currency => {
        const option = document.createElement('option');
        option.value = currency.currency;
        datalist.appendChild(option);
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const elements = getDOMElements();
    await convertValues(elements);
}

function handleSwapCurrencies(e) {
    e.preventDefault();
    const elements = getDOMElements();
    [elements.fromInput.value, elements.toInput.value] = [elements.toInput.value, elements.fromInput.value];
    convertValues(elements);
}

async function convertValues(elements = getDOMElements()) {
    try {
        if (!validateInputs(elements)) return;

        const conversionData = prepareConversionData(elements);
        const result = await performConversion(conversionData);

        updateUI(elements, result);
    } catch (error) {
        showError(error.message);
    }
}

function validateInputs(elements) {
    if (!elements.fromInput.value || !elements.toInput.value) {
        showError('Выберите валюты для конвертации');
        return false;
    }
    return true;
}

function prepareConversionData(elements) {
    return {
        from: elements.fromInput.value,
        to: elements.toInput.value,
        amount: elements.firstValue.value || 1
    };
}

async function performConversion(data) {
    const response = await fetch('/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error('Ошибка конвертации');
    return response.json();
}

function updateUI(elements, data) {
    elements.secondValue.value = data.result.toFixed(2);
    if (!elements.firstValue.value) {
        elements.firstValue.value = data.result ? 1 : '';
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.prepend(errorDiv);

    setTimeout(() => errorDiv.remove(), 3000);
}

function debounce(func, wait) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}