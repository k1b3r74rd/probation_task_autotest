import json
import pytest
import requests
import os
import logging

adresses = [('127.1.2.3', ''), ('localhost', '65535'), ('127.2.2.2', '123')]  # Адреса для проверки смены айпи-порта.
localhost_adresses = [('', ''), ('127.0.0.1', '17678'), ('localhost', '17678')]  # Адреса по умолчанию.


class Test_control:
    def test_adresses_localhost(self):
        """
        Тест на значения по умолчанию - 127.0.0.1:17678.
        """
        os.system('taskkill /im webcalculator.exe /f')
        os.system('webcalculator.exe start')

        response = requests.get('http://127.0.0.1:17678/api/state').json()
        assert (response.get('statusCode') == 0, f"Wrong status code - expected 0, got {response.get('statusCode')}")

    @pytest.mark.parametrize('ip, port', adresses)
    def test_adresses(self, ip, port):
        """
        Тест на смену адреса хоста/порта.
        """
        os.system(f'taskkill /im webcalculator.exe /f')
        os.system(f'webcalculator.exe start {ip} {port}')

        if port == '':
            response = requests.get(f'http://{ip}:17678/api/state').json()
            assert (response.get('statusCode') == 0, f"Wrong status code - expected 0, got {response.get('statusCode')}")
        else:
            response = requests.get(f'http://{ip}:{port}/api/state').json()
            assert (response.get('statusCode') == 0, f"Wrong status code - expected 0, got {response.get('statusCode')}")

    def test_restart(self):
        """
        Тест на возможность рестарта.
        """
        os.system(f'taskkill /im webcalculator.exe /f')
        os.system(f'webcalculator.exe start')

        os.system(f'webcalculator.exe restart')
        response = requests.get(f'http://127.0.0.1:17678/api/state').json()
        assert (response.get('statusCode') == 0, f"Wrong status code - expected 0, got {response.get('statusCode')}")

    def test_stop(self):
        """
        Тест на возможность остановки.
        """
        os.system('taskkill /im webcalculator.exe /f')
        os.system('webcalculator.exe start')

        os.system('webcalculator.exe stop')
        try:
            requests.get(f'http://127.0.0.1:17678/api/state')
        except Exception:  # Если ошибка при подключении - всё ок.
            pass
        else:
            pytest.fail("Server hasn't shut down")
