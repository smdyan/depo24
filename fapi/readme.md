## venv
pip install -r requirements.txt
## FAPI
run app in venv
```code
source .venv/bin/activate
fapi % uvicorn src.main:app --reload
```
Работа: 
1. запустить сервер
2. импортировать словари
3. создать вклады
4. изменения ставки (опционально)
5. пополнить вклад (опционально)
6. произвести начисления (начисление и выплата %, закрытие вклада)
