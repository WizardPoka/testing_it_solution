# app/scraper.py

# ==============================================================================

import requests
from bs4 import BeautifulSoup

# ==============================================================================

URL = "https://www.farpost.ru/vladivostok/service/construction/guard/+/Системы+видеонаблюдения/"

# ==============================================================================

def parse_adverts():
    """
    Парсинг первых 10 объявлений с FarPost
    """
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    adverts = []

    # Находим все объявления
    advert_elements = soup.find_all('tr', class_='bull-list-item-js', limit=10)
    
    for position, advert_element in enumerate(advert_elements, start=1):
        try:
            # Извлекаем данные из HTML
            advert_id = advert_element.get('data-doc-id', '0')
            title_element = advert_element.find('a', class_='bulletinLink bull-item__self-link auto-shy')
            title = title_element.get_text(strip=True) if title_element else "Неизвестно"
            author = advert_element.find('div', class_='address auto-shy').get_text(strip=True) if advert_element.find('div', class_='address auto-shy') else "Неизвестно"
            views_element = advert_element.find('span', class_='views nano-eye-text')
            views = int(views_element.get_text(strip=True)) if views_element else 0
            
            # Логирование информации об объявлении
            print(f"Parsed advert: ID={advert_id}, Title={title}, Author={author}, Views={views}, Position={position}")
            
            # Добавляем данные в список
            adverts.append({
                'title': title,
                'advert_id': int(advert_id),
                'author': author,
                'views': views,
                'position': position
            })
        except Exception as e:
            print(f"Ошибка при обработке объявления: {e}")
    
    return adverts

# ==============================================================================
