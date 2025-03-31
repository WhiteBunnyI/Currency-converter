let isInit = false;
let isMobile = false;
let currency_value = null;
let arrows = null;

document.addEventListener("DOMContentLoaded", initialization);
window.addEventListener("resize", check_resolution);

function initialization()
{
    arrows = document.querySelector("div.flex-container.currency-value img.arrows");
    currency_value = document.querySelector("div.flex-container.currency-value");
    isInit = true;
    check_resolution();
}

function check_resolution()
{
    if(!isInit) return;

    if(!isMobile && window.innerWidth < 1000)
    {
        setMobile();
        console.log("Ставим мобильную версию...");
    }
    else if(isMobile && window.innerWidth >= 1000)
    {
        setDesktop();
        console.log("Ставим десктопную версию...");
    }
}

function setMobile()
{
    
    isMobile = true;
    currency_value.style.flexFlow = "column";
    arrows.src = "./icons/sync_alt.svg";
    arrows.className = "mobile-arrows";
}

function setDesktop()
{
    isMobile = false;
    currency_value.style.flexFlow = "row";
    arrows.src = "./icons/arrows.svg";
    arrows.className = "arrows";

}