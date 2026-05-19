*** Settings ***
Library    SeleniumLibrary
Library    RequestsLibrary
Resource   variables.robot

*** Keywords ***
Otwórz aplikację
    Open Browser    ${BASE_URL}    ${BROWSER}
    ...    remote_url=${SELENIUM_HUB}
    Maximize Browser Window
    Set Selenium Timeout    ${TIMEOUT}
    Wait Until Page Contains    Price Tracker

Zamknij aplikację
    Close All Browsers

Przejdź do dashboardu
    Go To    ${BASE_URL}/dashboard
    Wait Until Page Contains Element    css:.stats

Kliknij przycisk "Dodaj produkt"
    Click Button    Dodaj produkt
    Wait Until Page Contains Element    css:form

Wypełnij formularz produktu
    [Arguments]    ${name}    ${url}
    Input Text    name=name    ${name}
    Input Text    name=url     ${url}

Zatwierdź formularz
    Click Button    Zapisz
    Wait Until Page Does Not Contain Element    css:form

Strona powinna zawierać produkt
    [Arguments]    ${name}
    Wait Until Page Contains    ${name}

Ustaw alert cenowy
    [Arguments]    ${threshold}    ${email}
    Click Element    css:[data-testid="add-alert"]
    Input Text    name=threshold    ${threshold}
    Input Text    name=email        ${email}
    Click Button    Zapisz alert
    Wait Until Page Contains    Alert ustawiony

Sprawdź API health
    Create Session    api    ${API_URL}
    ${response}=    GET On Session    api    /health
    Should Be Equal As Strings    ${response.status_code}    200
    Should Contain    ${response.text}    ok
