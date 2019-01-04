## Скрипт управления репликацией harbor с фильтром по лейблам

Параметры запуска

```console
Usage: ./harbor.api.repl.by.label.py -exec [inc|full]
```

---

![alt text](https://github.com/rlagutinhub/harbor.api.repl.by.label/blob/master/screen1.png)

---

* Проверка выполненная при предыдущем выполнение скрипта сохраняется в файл **harbor.api.repl.by.label.py.json** в папке расположения скрипта
* Перед выполнением, скрипт выполняет проверку монопольного запуска с помощью наличия **harbor.api.repl.by.label.py.pid** в папке расположения скрипта

**Режим выполнения full**

В данном случае, скрипт не делает сверку отличий из harbor.api.repl.by.label.py.json (если он существует) а создает новый harbor.api.repl.by.label.py.json, и запускает репликацию для всех политик репликации (есть новый образы для репликации или нет).

В результате успешного выполнения, основная функция main() вернет следующий статус:

![alt text](https://github.com/rlagutinhub/harbor.api.repl.by.label/blob/master/screen2.png)

**Режим выполнения inc**

В данном случае, скрипт выполняет сверку отличий из harbor.api.repl.by.label.py.json (если не существует, то будет выполнен full режим), и запускает репликацию только для тех политик репликации, где есть какие-либо изменения по сравнение с предыдущем выполнением (например есть новый образ для репликации).

В результате успешного выполнения, основная функция main() вернет следующий статус:

![alt text](https://github.com/rlagutinhub/harbor.api.repl.by.label/blob/master/screen3.png)

В случае, какой-либо ошибки, скрипт завершит свою работу с ошибкой **1** (pid файл будет удален)
