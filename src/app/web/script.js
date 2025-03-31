document.addEventListener("DOMContentLoaded", check_resolution);

function check_resolution()
{
    if(window.screen.width < 1000)
    {
        setMobile();
    }
}

function setMobile()
{
    let currency_value = document.querySelector("div.flex-container.currency-value");
    currency_value.style.flexFlow = "column";

}