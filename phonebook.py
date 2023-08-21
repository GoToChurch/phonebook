import json

from pathlib import Path
from re import match


class Phonebook:
    def __init__(self):
        self.path = Path("data.json")
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.personal_numbers = list(map(lambda entity: entity["personal_number"], self.data))
        self.listen()

    def listen(self):
        while (True):
            user_input = input(
                "Введите цифру команды чтобы ее выполнить: \n" +
                "1. Показать записи \n2. Добавление записи \n" +
                "3. Редактирование записи \n4. Поиск записей\n5. Выход\n"
            )
            if user_input == "1":
                self.show()
            elif user_input == "2":
                self.add()
            elif user_input == "3":
                self.update()
            elif user_input == "4":
                print(self.search())
            elif user_input == "5":
                print("Осущетвляется выход")
                break
            else:
                print("Такой команды не существует, повторите попытку")

    """ Позволяет посмотреть все записи или одну страницу. На одной странице
    содержатся 20 записей. """
    def show(self):
        print("Каждая страница содержит 20 записей")
        page = input("Какую страницу хотите посмотреть (оставьте пустым если все):\n")

        return_data = {}
        page_number = 1
        page_entities = []

        for entity in self.data:
            if not page_entities:
                return_data.update({
                    f"page{page_number}": []
                })

            page_entities.append(entity)

            if len(page_entities) == 20 or entity == self.data[-1]:
                return_data.update({
                    f"page{page_number}": page_entities
                })
                page_number += 1
                page_entities = []

        if page:
            print(self.dump(return_data.get(f"page{page}")))
        else:
            print(self.dump(return_data))

    """ Позволяет создать и сохранить новую запись в записную книгу. """
    def add(self):
        data_to_add = self.get_new_entity()

        if not self.check_if_exists(self.data, data_to_add):
            self.data.append(data_to_add)
            self.save(self.data)
            self.refresh_data()
            print(f"Добавлена запись:\n {self.dump(data_to_add)}")

    """ Позволяет обновить существующую запись в записной книге. """
    def update(self):
        print("Для начала найдем нужную Вам запись")
        search_list = json.loads(self.search())
        entity_number = 0

        if (len(search_list) > 1):
            print(self.dump(search_list))
            entity_number = int(input("Укажите номер записи которую нужно отредактировать\n")) - 1

        entity_to_update = search_list[entity_number]

        print(f"Запись для редактирования:\n {self.dump(entity_to_update)}")
        print("Остаьте поле пустым, если хотите оставить поле без изменений")

        new_entity = self.get_new_entity(parent_entity=entity_to_update)

        for i in range(0, len(self.data)):
            if self.compare(self.data[i], entity_to_update):
                self.data[i] = new_entity

        self.save(self.data)
        self.refresh_data()
        print(f"Была отредактирована запись:\n {self.dump(entity_to_update)}\n "
              f"Новая запись: \n {self.dump(new_entity)}")

    """ Позволяет выполнить поиск по записной книге по одному или 
    нескольким параметрам. """
    def search(self):
        print("Оставьте поле пустым если его не надо учитывать при поиске")

        search_results = []
        data = json.loads(self.path.read_text(encoding="utf-8"))

        search_params = self.get_new_entity(validate=False)

        for entity in data:
            if self.compare(entity, search_params):
                search_results.append(entity)

        return json.dumps(search_results, ensure_ascii=False, indent=4)

    """ Валадирует поля отчества, номера личного телефона и рабочего номера. """
    def validate(self, entity):
        message = ""
        if not match(r"\w+ич$|\w+на$", entity["surname"]):
            message += "Неправильный формат отчества\n"
        if not match(r"\+7\d{10}", entity["personal_number"]):
            message += "Неправильный формат номера личного телефона\n"
        if not match(r"\d{7}", entity["work_number"]):
            message += "Неправильный формат номера рабочего телефона\n"
        if entity["personal_number"] in self.personal_numbers:
            message += "Номер личного телефона должен быть уникальным\n"
        if message:
            message += "Повторите попытку\n"
            print(message)
            return False
        return True

    """ Проверяет, существует ли переданная запись (entity) 
    в переданном списке (data)."""
    def check_if_exists(self, data, entity):
        if entity in data:
            print("Такая запись уже существует")
            return True

        return False

    """ Сравнивает запись (entity) с переданными параметрами поиска (search_params).
    Возваращает True если поля записи и соответствующие поля параметра поиска
    совпадают. В обратном случае возвращает False. """
    def compare(self, entity, search_params):
        for key, value in entity.items():
            if search_params[key]:
                if not search_params[key].lower() == value.lower():
                    return False

        return True

    """ Сохраняет переданный список (data) в файл по пути self.path """
    def save(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=4),
                        encoding="utf-8")

    """ Позволяет получить запись на основе введенных пользователем информации. 
    Если validate=True, переданные данные валидируются методом validate().
    Если parent_entity != None, то неуказанные пользователем поля получают
    значения, равными значению соответствующих полей из parent_entity."""
    def get_new_entity(self, validate=True, parent_entity=None):
        lastname = input("Введите фамилию (например, Иванов):\n")
        name = input("Введите имя (например, Борис):\n")
        surname = input("Введите отчество (например, Павлович):\n")
        organisation = input(
            "Введите название организации (например, Газпром):\n")
        work_number = input(
            "Введите номер рабочего телефона (например, 2996569):\n")
        personal_number = input("Введите номер личного телефона "
                                "(например, +79651234567):\n")

        new_entity = self.create_new_entity(
                    lastname, name, surname, organisation, work_number,
                    personal_number
                )

        if parent_entity:
            for key, value in new_entity.items():
                if not value:
                    new_entity[key] = parent_entity[key]

        if validate:
            if self.validate(new_entity):
                return new_entity
            else:
                self.get_new_entity()
        else:
            return new_entity

    """ Создает новую запись на основе введенных пользователем информации. """
    def create_new_entity(self, lastname, name, surname, organisation,
                          work_number, personal_number):
        return {
            "lastname": lastname,
            "name": name,
            "surname": surname,
            "organisation": organisation,
            "work_number": work_number,
            "personal_number": personal_number,
        }

    """ Обновляет поля self.data и self.personal_numbers. """
    def refresh_data(self):
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.personal_numbers = list(
            map(lambda entity: entity["personal_number"], self.data))

    """ Вызывает метод json.dumps для переданного списка (data). """
    def dump(self, data):
        return json.dumps(data, ensure_ascii=False, indent=4)

Phonebook()