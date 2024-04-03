import json
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import tqdm
from task2 import path_to_file


@path_to_file(path='task3_hh.log')
def gen_headers():
    headers = Headers(browser='chrome', os='win')
    return headers.generate()


@path_to_file(path='task3_hh.log')
def get_count_of_pages():
    response = requests.get(url=base_url, headers=gen_headers())
    html_hh_data = response.text
    base_soup = BeautifulSoup(html_hh_data, 'lxml')

    """ Находим количество страниц с вакансиями """
    page_tag = base_soup.find('div', class_='pager').find_all('a')[-2]
    count_of_pages = int(page_tag.find('span').text.strip())

    print(f'Найдено {count_of_pages} страниц с вакансиями.\n'
          f'Пожалуйста, дождитесь завершения операции.')
    return count_of_pages


@path_to_file(path='task3_hh.log')
def write_json(data):
    with open("hh.json", "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@path_to_file(path='task3_hh.log')
def getting_required_data():
    required_data = []
    for page in tqdm.trange(get_count_of_pages(), desc='Собираем информацию'):

        url = f"{base_url}&page={page}"
        html_data = requests.get(url=url, headers=gen_headers()).text
        main_soup = BeautifulSoup(html_data, 'lxml')

        vacancy_tags = main_soup.find_all('div', class_='vacancy-serp-item-body__main-info')

        for vacancy_tag in vacancy_tags:
            position = vacancy_tag.find('span', class_='serp-item__title-link serp-item__title').text
            link = vacancy_tag.find('a', class_='bloko-link', attrs={'target': '_blank'})['href']
            city = vacancy_tag.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]

            company_tag = vacancy_tag.find('span', class_='serp-item__title-link serp-item__title',
                                           attrs={'data-qa': 'serp-item__title'})
            company = " ".join(company_tag.text.split())

            salary_tag = vacancy_tag.find('span', class_='bloko-header-section-2',
                                          attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary_tag is not None and '$' in salary_tag.text:
                salary = " ".join(salary_tag.text.split())

                vacancy_data = requests.get(link, headers=gen_headers()).text
                vacancy_soup = BeautifulSoup(vacancy_data, 'lxml')

                description_tag = vacancy_soup.find('div', attrs={'data-qa': 'vacancy-description'})
                if description_tag is None:
                    pass
                else:
                    description = " ".join(description_tag.text.split())
                    if 'django' in description.lower() or 'flask' in description.lower():
                        required_data.append({
                                'position': position,
                                'link': link,
                                'company': company,
                                'city': city,
                                'salary': salary,
                                'description': description
                            })

    write_json(required_data)
    print('Сбор и обработка информации завершены.')


base_url = 'https://spb.hh.ru/search/vacancy?area=1&area=2&text=python'


if __name__ == '__main__':
    getting_required_data()
