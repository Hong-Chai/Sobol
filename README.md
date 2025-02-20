# SOBOL: Assault — тактическая игра про спецназ

SOBOL: Assault — тактическая игра, в которой игроки управляют отрядом спецназа на различных уровнях и в разных комнатах. Созданная с помощью Pygame, эта игра предлагает уникальное сочетание стратегии и экшена.

В игре вы командуете отрядом спецназа Sobol, который перемещается по сложным средам. Игроки должны использовать тактические решения, чтобы зачищать комнаты, избегать препятствий и выполнять миссии. SOBOL: Assault, ориентированная на реализм и стратегический игровой процесс, обеспечивает захватывающий опыт в мире спецопераций.

Ключевые особенности включают:
- Захватывающий сюжет
- Тактическая механика зачистки комнат
- Прогрессивное разблокирование навыков
- Реалистичные звуковые эффекты
- Подсчет очков

## Структура репозитория

- `main.py`: Основная точка входа и основная игровая логика
- `data/`: Каталог, содержащий игровые ресурсы (изображения, звуки)

## Инструкции по использованию

### Установка

1. Убедитесь, что в вашей системе установлен Python 3.13+.

2. Клонируйте репозиторий или загрузите исходный код.

3. Установите requirements:
```
pip install -r requirements.txt
```

### Запуск игры

Чтобы запустить игру, перейдите в каталог проекта и выполните:

```
python main.py
```

### Управление

- Используйте мышь и щелкните, куда вы хотите переместить команду Соболя.
- Щелкайте на дверь чтобы начать штурм!

### Конфигурация

Базовую конфигурацию игры можно настроить в `main.py`:

- `SCREEN_WIDTH` и `SCREEN_HEIGHT`: установите размер игрового окна
- `FPS`: отрегулируйте частоту кадров игры
- `TILE_SIZE`: измените размер игровых плиток

### Устранение неполадок

Если у вас возникли проблемы с отсутствующими ресурсами:
1. Убедитесь, что все файлы изображений присутствуют в каталоге `data/`.
2. Проверьте, что имена файлов в вызовах `load_image()` соответствуют фактическим именам файлов.

Для проблем с производительностью:
1. Уменьшите константу `FPS` в `main.py`.
2. Уменьшите `SCREEN_WIDTH` и `SCREEN_HEIGHT` для более низкого разрешения.

Для игровых моментов:
1. Если после нажатия на дверь игра "зависла", то проверьте, не свернуто ли окно штурма.
2. Если при испольвании exe файла штрум закачивается раньше, чем 10 секунд, то значит игра не может получить доступ к модюлю времени ПК, перекомпилируйте exe для своей сиситемы.

## Поток данных

Поток данных игры следует этой общей схеме:

1. Инициализация игры (настройка Pygame, загрузка ресурсов)
2. Взиамодейтсвие с главным меню
3. Основной цикл игры:
- Обработка пользовательского ввода
- Обновление состояния игры (движение игрока, столкновения)
- Отображение игровых объектов
- Отображение обновлений
4. Завершение игры

```
[Начало игры] -> [Инициализация Pygame] -> [Загрузка ресурсов] -> [Создание уровня]
  |
  v
[Основной цикл игры]      <->    [Открыто меню штурма]
  |                                 |
  v                                 v
[Обновление состояния игры]    [Подтверждение параметров и заморозка основной линии]
  |                                 |
  v                                 v
[Проверка столкновений]       ["Анимация" штурма]
  |
  v
[Отображение игровых объектов]
  |
  v
[Отображение обновлений]
  |
  v
[Проверка окончания игры]
  |
  v
[Конец игры]
```

Примечание: текущая реализация фокусируется на движении игрока и базовой структуре уровня. В будущих обновлениях будут представлены более сложные игровые механики и дополнительные потоки данных для таких функций, как искусственный интеллект противника и особые способности.
