import json
import pytest
import requests
import os

# Значения переменных для тестов в формате {x, y, ожидаемый код статуса}.
test_numbers = [(42, 34, 0), (-42, 34, 0), (-42, -34, 0), (42, 1, 0), (1, 34, 0), (0, 34, 0),
                (None, 1, 3), (4.2, 1, 3), ('x', 1, 3), ((42, 34), 1, 3), (json.dumps({'x': 42, 'y': 34}), 1, 3),
                (2147483647+2, 1, 4), (-2147483648-2, 1, 4)]

test_numbers_additional_multi = [(42, 0, 0), (0, 0, 0)]  # Доп тесты для умножения.
test_numbers_additional_div = [(42, 0, 1), (0, 34, 0),
                               (42, 1, 0), (1, 34, 0)]  # Доп тесты для делений.

tasks = ['addition', 'multiplication', 'division', 'remainder']
div_tasks = ['division', 'remainder']


@pytest.fixture(scope="module", params=tasks)  # Все операции.
def task(request):
    return request.param


@pytest.fixture(scope="module", params=div_tasks)  # Операции деления для доп. тестов.
def div_task(request):
    return request.param


def calc(x, y, task):
    if task == 'addition':
        return int(x + y)
    elif task == 'multiplication':
        return int(x * y)
    elif task == 'division':
        return int(x // y)
    elif task == 'remainder':
        return int(x % y)


def server_launch():
    """
    Костыль для запуска сервера.
    """
    os.system('taskkill /im webcalculator.exe /f')
    os.system('webcalculator.exe start')


class Test_calculations:
    # TODO: async?
    server_launch()

    @pytest.mark.parametrize("x, y, expected_statusCode", test_numbers)
    def test_number_operations(self, x, y, expected_statusCode, task):
        """
        Тест на правильность вычисления и код статуса.
        """
        errors = []

        data_json = json.dumps({'x': x, 'y': y})
        response = requests.post(f'http://localhost:17678/api/{task}', data=data_json).json()

        if not (response.get('statusCode') == expected_statusCode):  # Проверка кода статуса.
            errors.append(f"Wrong status code - expected {expected_statusCode}, got {response.get('statusCode')}")

        if response.get('result') is not None:  # Если имеется результат - проверяем.
            if not (response.get('result') == calc(x, y, task)):
                errors.append(f"Wrong answer - expected {calc(x, y, task), type(calc(x, y, task))}, got {response.get('result')}")

        assert not errors, ' | '.join(errors)

    @pytest.mark.parametrize("x, y, expected_statusCode", test_numbers_additional_multi)
    def test_number_operations_extra_multi(self, x, y, expected_statusCode):
        """
        Дополнительный тест неординарных кейсов для умножения.
        """
        errors = []
        task = 'multiplication'

        data_json = json.dumps({'x': x, 'y': y})
        response = requests.post(f'http://localhost:17678/api/{task}', data=data_json).json()

        if not (response.get('statusCode') == expected_statusCode):  # Проверка кода статуса.
            errors.append(f"Wrong status code - expected {expected_statusCode}, got {response.get('statusCode')}")

        if response.get('result') is not None:  # Если имеется результат - проверяем.
            if not (response.get('result') == calc(x, y, task)):
                errors.append(f"Wrong answer - expected {calc(x, y, task), type(calc(x, y, task))}, got {response.get('result')}")

        assert not errors, ' | '.join(errors)

    @pytest.mark.parametrize("x, y, expected_statusCode", test_numbers_additional_div)
    def test_number_operations_extra_div(self, x, y, expected_statusCode, div_task):
        """
        Дополнительный тест неординарных кейсов для делений.
        """
        errors = []

        data_json = json.dumps({'x': x, 'y': y})
        response = requests.post(f'http://localhost:17678/api/{div_task}', data=data_json).json()

        if not (response.get('statusCode') == expected_statusCode):  # Проверка кода статуса.
            errors.append(f"Wrong status code - expected {expected_statusCode}, got {response.get('statusCode')}")

        if response.get('result') is not None:  # Если имеется результат - проверяем.
            if expected_statusCode == 1:  # Избегаем деления на 0 в коде программы.
                pass
            elif not (response.get('result') == calc(x, y, div_task)):
                errors.append(f"Wrong answer - expected {calc(x, y, div_task)}, got {response.get('result')}")

        assert not errors, ' | '.join(errors)

    def test_server_operations(self, task):
        """
        Тест ответов сервера на неправильные запросы.
        """
        errors = []

        data_json_nokey = json.dumps({'x': 42})
        data_raw = {'x': 42, 'y': 34}

        # Отправка запроса НЕ json формата.
        response = requests.post(f'http://localhost:17678/api/{task}', data=data_raw).json()
        if not (response.get('statusCode') == 5):
            errors.append(f"Wrong status code - expected {5}, \
                                                     got {response.get('statusCode')}")

        # Отправка запроса с отсутствующим ключом.
        response = requests.post(f'http://localhost:17678/api/{task}', data=data_json_nokey).json()
        if not (response.get('statusCode') == 2):
            errors.append(f"Wrong status code - expected {2}, \
                                                     got {response.get('statusCode')}")

        # Отправка неправильного запроса
        response = requests.get(f'http://localhost:17678/api/{task}').json()
        if not (response.get('statusCode') == 5):
            errors.append(f"Wrong status code - expected {5}, \
                                                     got {response.get('statusCode')}")

        assert not errors, ' | '.join(errors)

        # TODO: options?
