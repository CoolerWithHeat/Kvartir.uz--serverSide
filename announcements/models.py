from django.db import models

apartment_type = (
    ('продается', 'продается'),
    ('в аренду', 'в аренду'),
)

regions = ['Чиланзар', 'Мирабад', 'Сергели', 'Учтепинский',  'Мирзо-Улугбек',  'Шайхантаур', 'Юнусабад', 'Яккасарай', 'Яшнабад', 'Алмазар']

region_option = (
    ('Чиланзар', 'Чиланзар'),
    ('Мирабад', 'Мирабад'),
    ('Сергели', 'Сергели'),
    ('Учтепинский', 'Учтепинский'),
    ('Бектемир', 'Бектемир'),
    ('Мирзо-Улугбек', 'Мирзо-Улугбек'),
    ('Шайхантаур', 'Шайхантаур'),
    ('Юнусабад', 'Юнусабад'),
    ('Яккасарай', 'Яккасарай'),
    ('Яшнабад', 'Яшнабад'),
    ('Алмазар', 'Алмазар'),
)

def get_chilanzar_sections():
    indexed_value = {}
    data_list = []
    additional_ones = ['Наккошлик', 'Думбрабод', 'Квартал Г9а', 'Квартал Ц', 'Квартал Е', 'Квартал И']
    for i in range(1, 32 + len(additional_ones) + 1):
        if i <= 31:
            prefix = "(Алгоритм)" if 26 < i <= 31 else ''
            data = f"{i}-Квартал{f' {prefix}' if prefix else ''}"
            data_list.append(data)
            indexed_value[data] = i
        else:
            secondary_index = i - 32
            data = additional_ones[secondary_index] if secondary_index < len(additional_ones) else ''
            if data:
                data_list.append(data)
                indexed_value[data] = i
    return {'indexedValue': indexed_value, 'dataList': data_list}

def get_chilanzar_options(data_list):
    choices = [(index, item) for index, item in enumerate(data_list, start=1)]
    return choices

bathroom_options = (
    ('Раздельный', 'Раздельный'),
    ('Совмещенный', 'Совмещенный'),
)

room_layout_options = (
    ('Раздельное', 'Раздельное'),
    ('Cмежные', 'Cмежные'),
    ('Cмежные-раздельные', 'Cмежные-раздельные'),
)

construction_materials_options = (
    ('Кирпичный', 'Кирпичный'),
    ('Панельный', 'Панельный'),
    ('Монолитный', 'Монолитный'),
)

class client_numbers(models.Model):
    number = models.CharField(max_length=18, default='+998', blank=False, null=False,  verbose_name='вторичный номер')
    def __str__(self):
        return self.number

class phone_number(models.Model):
    number = models.CharField(max_length=18, default='+998997010098', blank=False, null=False,  verbose_name='вторичный номер')
    
    class Meta:
        verbose_name_plural = "сохраненные вторичный номеры"   

    def __str__(self):
        return self.number

class Reiltor_Number(models.Model):
    reiltor_name = models.CharField(max_length=25, default='Масуд', blank=False, null=False, verbose_name='имя риэлтора')
    main_reiltor_number = models.CharField(max_length=18, default='+998997010098', blank=False, null=False, verbose_name='Основной номер')
    secondary_numbers = models.ManyToManyField(phone_number, verbose_name='вторичный номер', blank=True)

    class Meta:
        verbose_name_plural = "контакт риэлтора"   

    def __str__(self):
        return f"Reiltor {self.reiltor_name} --> {self.main_reiltor_number}"

class apartment_images(models.Model):
    file = models.FileField(default=None, blank=False, upload_to='images/')
    
    def __str__(self):
        return f'{self.file.url}'
    
    class Meta:
        verbose_name_plural = "Загруженные Фотки"  

class floor(models.Model):
    building_total_floor = models.IntegerField(blank=False, null=False, verbose_name='Этажность здания')
    apartment_floor = models.IntegerField(default=None, blank=False, null=False, verbose_name='этаж квартиры')
    apartment_room_count = models.IntegerField(blank=False, null=False, verbose_name='количество комнаты в квартире')
    
    def __str__(self):
        return f'{self.apartment_room_count}/{self.apartment_floor}/{self.building_total_floor}'

    class Meta:
        verbose_name_plural = "Этажи"

class Announcement(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, verbose_name='цена')
    thumbnail = models.FileField(default='Any Picture', blank=False, null=False, verbose_name='миниатюра')
    description = models.TextField(default='нет описания', max_length=620, blank=False, null=False, verbose_name='описание')
    images = models.ManyToManyField(apartment_images, verbose_name='изображений кв')
    square_meters = models.FloatField(blank=False, null=False, verbose_name='кв метр')
    apartment_region = models.CharField(max_length=35, choices=region_option, default='Чиланзар', blank=False, null=False, verbose_name="район")
    announcement_type = models.CharField(max_length=35, choices=apartment_type, default='продается', blank=False, null=False, verbose_name='объявление')
    floor = models.ForeignKey(floor, on_delete=models.CASCADE, default=None, blank=False, null=False, verbose_name='этаж')
    bathroom = models.CharField(max_length=100, default='Раздельный', choices=bathroom_options, blank=False, null=False, verbose_name='структура санузеля')
    kitchen_size = models.CharField(max_length=100, blank=True, null=True, verbose_name='метр.к кухня') 
    room_count = models.IntegerField(blank=False, null=False, verbose_name='количество комнат')
    construction_material = models.CharField(max_length=100, default='Раздельное', choices=construction_materials_options, blank=False, null=False, verbose_name='Материал квартиры')
    kvartal = models.IntegerField(choices=get_chilanzar_options(get_chilanzar_sections()['dataList']), default=1, blank=False, verbose_name='Квартал')
    landmark = models.CharField(max_length=40, blank=False, null=False, verbose_name="Ориентир")
    room_layout = models.CharField(max_length=100, default='Раздельное', choices=room_layout_options, blank=False, null=False, verbose_name="Планировка")
    end_wall_structure = models.BooleanField(default=False, blank=False, null=False, verbose_name="Торец")
    mortgage_deal_possible = models.BooleanField(default=False, blank=False, null=False, verbose_name="Ипотека")
    
    def __str__(self):
        kvartal = ''
        if self.apartment_region == 'Чиланзар':
            if self.kvartal > 31:
                data = get_chilanzar_sections()['dataList']
                kvartal = f', {data[self.kvartal-1]}'
            else:
                kvartal = f', {self.kvartal}-Квартал'
        return f'{self.apartment_region}{kvartal}  <----> за ${self.price}${"/месяц" if self.announcement_type == "в аренду" else ""}'
    
    class Meta:
        verbose_name_plural = "Объявления"