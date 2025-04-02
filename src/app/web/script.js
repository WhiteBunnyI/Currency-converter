let minDesktopResolution = 1000;

let isInit = false;
let isMobile = false;
let currency_value = null;
let arrows = null;
let switchCurrency = null;

document.addEventListener("DOMContentLoaded", initialization);
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