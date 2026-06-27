# security_tester.py
import requests
import time
from urllib.parse import urljoin

class SecurityTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
    
    def log(self, test_name, status, details=""):
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        self.results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
    
    def test_path_traversal(self):
        """Тест на обход директорий"""
        print("\n🔍 Тест 1: Path Traversal")
        payloads = [
            '../../../etc/passwd',
            '..%2F..%2F..%2Fetc%2Fpasswd',
            '....//....//....//etc/passwd',
            '..\\..\\..\\windows\\win.ini'
        ]
        
        for payload in payloads:
            try:
                url = urljoin(self.base_url, f'search/{payload}')
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200 and any(
                    keyword in response.text.lower() 
                    for keyword in ['root:x', '[extensions]', 'django.settings']
                ):
                    self.log(f"Path traversal: {payload}", "FAIL", "Файл прочитан!")
                    return
                elif response.status_code == 500:
                    self.log(f"Path traversal: {payload}", "FAIL", "Ошибка сервера")
                    return
            except Exception as e:
                pass
        
        self.log("Path Traversal", "PASS", "Уязвимость не обнаружена")
    
    def test_sql_injection(self):
        """Тест на SQL инъекции"""
        print("\n🔍 Тест 2: SQL Injection")
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' AND '1'='1",
            "1' OR '1'='1' --",
            "admin' --"
        ]
        
        for payload in payloads:
            try:
                url = urljoin(self.base_url, f'search/{payload}')
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 500:
                    self.log("SQL Injection", "FAIL", f"Ошибка БД при: {payload}")
                    return
                    
                # Проверка на уязвимость по времени (blind SQL)
                start = time.time()
                response = self.session.get(url, timeout=5)
                elapsed = time.time() - start
                
                if elapsed > 2:  # Если запрос долгий
                    self.log("SQL Injection", "⚠️", f"Подозрительная задержка: {elapsed:.2f}s")
                    
            except Exception:
                pass
        
        self.log("SQL Injection", "PASS", "Уязвимость не обнаружена")
    
    def test_xss(self):
        """Тест на XSS (межсайтовый скриптинг)"""
        print("\n🔍 Тест 3: XSS")
        payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert("XSS")',
            '"><script>alert(1)</script>',
            '<svg/onload=alert(1)>'
        ]
        
        for payload in payloads:
            try:
                url = urljoin(self.base_url, f'search/{payload}')
                response = self.session.get(url, timeout=5)
                
                if payload in response.text and response.status_code == 200:
                    self.log("XSS", "FAIL", f"Код выполняется: {payload[:30]}")
                    return
            except Exception:
                pass
        
        self.log("XSS", "PASS", "Уязвимость не обнаружена")
    
    def test_ssrf(self):
        """Тест на SSRF"""
        print("\n🔍 Тест 4: SSRF")
        payloads = [
            'http://169.254.169.254/latest/meta-data/',  # AWS metadata
            'http://localhost:8000/admin/',
            'http://127.0.0.1:8000/',
            'file:///etc/passwd',
            'http://internal.site/api/'
        ]
        
        for payload in payloads:
            try:
                url = urljoin(self.base_url, f'search/{payload}')
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.log("SSRF", "FAIL", f"Доступен внешний запрос: {payload}")
                    return
            except Exception:
                pass
        
        self.log("SSRF", "PASS", "Уязвимость не обнаружена")
    
    def test_dos(self):
        """Тест на DoS (Denial of Service)"""
        print("\n🔍 Тест 5: DoS")
        long_payload = 'a' * 10000 + '/' + 'b' * 10000
        
        try:
            url = urljoin(self.base_url, f'search/{long_payload}')
            start = time.time()
            response = self.session.get(url, timeout=10)
            elapsed = time.time() - start
            
            if elapsed > 5:
                self.log("DoS", "⚠️", f"Медленный ответ: {elapsed:.2f}s")
            elif response.status_code == 413 or response.status_code == 414:
                self.log("DoS", "PASS", "Защита от длинных запросов есть")
            else:
                self.log("DoS", "PASS", f"Обработан за {elapsed:.2f}s")
        except requests.Timeout:
            self.log("DoS", "FAIL", "Сервер завис от длинного запроса!")
        except Exception as e:
            self.log("DoS", "⚠️", f"Ошибка: {e}")
    
    def test_command_injection(self):
        """Тест на инъекцию команд ОС"""
        print("\n🔍 Тест 6: Command Injection")
        payloads = [
            '; ls -la',
            '| whoami',
            '`id`',
            '$(echo test)',
            '; cat /etc/passwd'
        ]
        
        for payload in payloads:
            try:
                url = urljoin(self.base_url, f'search/{payload}')
                response = self.session.get(url, timeout=5)
                
                if any(cmd in response.text for cmd in ['root:', 'uid=', 'test']):
                    self.log("Command Injection", "FAIL", "Команда выполнилась!")
                    return
            except Exception:
                pass
        
        self.log("Command Injection", "PASS", "Уязвимость не обнаружена")
    
    def test_headers_security(self):
        """Проверка security-заголовков"""
        print("\n🔍 Тест 7: Security Headers")
        try:
            response = self.session.get(self.base_url, timeout=5)
            headers = response.headers
            
            security_headers = {
                'X-Frame-Options': 'Защита от clickjacking',
                'X-Content-Type-Options': 'Защита от MIME sniffing',
                'Content-Security-Policy': 'CSP защита',
                'X-XSS-Protection': 'XSS защита',
                'Strict-Transport-Security': 'HSTS'
            }
            
            missing_headers = []
            for header, description in security_headers.items():
                if header not in headers:
                    missing_headers.append(f"{header} ({description})")
            
            if missing_headers:
                self.log("Security Headers", "⚠️", f"Отсутствуют: {', '.join(missing_headers)}")
            else:
                self.log("Security Headers", "PASS", "Все заголовки на месте")
                
        except Exception as e:
            self.log("Security Headers", "FAIL", f"Ошибка: {e}")
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("="*60)
        print(f"🔐 Тестирование безопасности: {self.base_url}")
        print("⚠️  Используйте ТОЛЬКО на своих сайтах!")
        print("="*60)
        
        self.test_path_traversal()
        self.test_sql_injection()
        self.test_xss()
        self.test_ssrf()
        self.test_dos()
        self.test_command_injection()
        self.test_headers_security()
        
        # Итоговый отчет
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("="*60)
        
        failed = [r for r in self.results if r['status'] == 'FAIL']
        warnings = [r for r in self.results if r['status'] == '⚠️']
        
        print(f"✅ Пройдено: {len(self.results) - len(failed) - len(warnings)}")
        print(f"⚠️  Предупреждений: {len(warnings)}")
        print(f"❌ Критических уязвимостей: {len(failed)}")
        
        if failed:
            print("\n🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for fail in failed:
                print(f"  - {fail['test']}: {fail['details']}")
        
        if warnings:
            print("\n🟡 РЕКОМЕНДАЦИИ:")
            for warn in warnings:
                print(f"  - {warn['test']}: {warn['details']}")
        
        print("="*60)

# Использование
if __name__ == "__main__":
    # Укажите URL вашего сайта
    tester = SecurityTester("http://127.0.0.1:8000")  # или ваш URL
    tester.run_all_tests()