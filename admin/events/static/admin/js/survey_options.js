// Функция для добавления полей ответов в опросах
(function ($) {
  'use strict';

  function logToServer(level, message) {}

  $(document).ready(function () {
    // Проверяем, находимся ли мы в режиме просмотра (readonly)
    var isReadOnly =
      $('body').hasClass('change-form') && !$('.submit-row').length;

    $('[data-options]').each(function () {
      var dataOptions = $(this).attr('data-options');
      var questionForm = $(this).closest('.inline-related');
      if (questionForm.length > 0) {
        questionForm.attr('data-options', dataOptions);
      }
    });

    function createOptionFields(questionForm, formIndex, options) {
      var textField = questionForm.find(
        'textarea[name="questions-' + formIndex + '-text"]'
      );

      if (textField.length === 0) {
        textField = questionForm.find('textarea[name*="text"]');
      }

      if (textField.length === 0) {
        textField = questionForm.find('input[type="text"]').first();
      }

      if (textField.length === 0) {
        return;
      }

      var fieldContainer = textField.closest('.form-row').parent();

      var optionsHeader = $('<h3>Варианты ответов</h3>');
      optionsHeader.css({
        'margin-top': '15px',
        'margin-bottom': '10px',
      });
      if (fieldContainer.find('h3:contains("Варианты ответов")').length === 0) {
        fieldContainer.append(optionsHeader);
      }

      var optionsContainer = $('<div class="options-container"></div>');
      optionsContainer.css({
        border: '1px solid #ddd',
        padding: '10px',
        'margin-bottom': '15px',
        'background-color': 'transparent',
      });

      var existingContainer = fieldContainer.find('.options-container');
      if (existingContainer.length > 0) {
        optionsContainer = existingContainer;
      } else {
        fieldContainer.append(optionsContainer);
      }

      optionsContainer.empty();
      if (options.length === 0) {
        // Проверяем, является ли это новой формой (добавленной через кнопку "Добавить еще один вопрос")
        var isNewForm =
          questionForm.hasClass('last-related') ||
          questionForm.hasClass('dynamic-questions') ||
          questionForm.find('input[name$="-id"]').val() === '';

        if (isNewForm) {
          options = [
            { order: 1, text: '' },
            { order: 2, text: '' },
          ];
        } else {
          // Для существующей формы без вариантов создаем два стандартных варианта
          options = [
            { order: 1, text: 'Вариант 1' },
            { order: 2, text: 'Вариант 2' },
          ];
        }
      }

      // Создаем поля для каждого варианта ответа
      for (var i = 0; i < options.length; i++) {
        var option = options[i];
        var optionIndex = option.order;

        // Создаем новое поле
        var fieldRow = $(
          '<div class="form-row field-option_' + optionIndex + '"></div>'
        );
        var fieldInner = $('<div></div>');
        var fieldFlex = $('<div class="flex-container"></div>');
        var fieldLabel = $(
          '<label for="id_questions-' +
            formIndex +
            '-option_' +
            optionIndex +
            '">Вариант ответа ' +
            optionIndex +
            ':</label>'
        );

        // Если режим просмотра, создаем span вместо input
        var fieldInput;
        if (isReadOnly) {
          fieldInput = $(
            '<span class="readonly">' + (option.text || '') + '</span>'
          );
        } else {
          fieldInput = $(
            '<input type="text" name="questions-' +
              formIndex +
              '-option_' +
              optionIndex +
              '" id="id_questions-' +
              formIndex +
              '-option_' +
              optionIndex +
              '" class="option-field" value="' +
              (option.text || '') +
              '">'
          );
        }

        var deleteButton;
        if (!isReadOnly) {
          deleteButton = $(
            '<a href="#" class="button delete-option" style="margin-left: 10px; color: red;">Удалить</a>'
          );

          // Обработчик клика для удаления поля
          deleteButton.on('click', function (e) {
            e.preventDefault();

            // Проверяем, сколько полей осталось
            var remainingFields = optionsContainer.find(
              'input[class="option-field"]'
            ).length;
            if (remainingFields <= 2) {
              alert('Должно быть минимум два варианта ответа');
              return;
            }

            // Удаляем поле
            $(this).closest('.form-row').remove();

            // Обновляем JSON с вариантами ответов
            updateOptionsJson(questionForm, formIndex);
          });

          // Обработчик изменения значения поля
          fieldInput.on('input', function () {
            // Обновляем JSON с вариантами ответов при изменении значения
            updateOptionsJson(questionForm, formIndex);
          });
        }

        // Собираем все вместе
        fieldFlex.append(fieldLabel, fieldInput);

        if (!isReadOnly && (optionIndex > 2 || options.length > 2)) {
          fieldFlex.append(deleteButton);
        }

        fieldInner.append(fieldFlex);
        fieldRow.append(fieldInner);

        // Добавляем поле в контейнер
        optionsContainer.append(fieldRow);
      }

      // Добавляем кнопку для добавления нового поля только если не режим просмотра
      if (!isReadOnly) {
        var addButton = $(
          '<a href="#" class="button add-option">+ Добавить вариант ответа</a>'
        );
        addButton.css({
          'margin-top': '10px',
          display: 'inline-block',
          'margin-bottom': '10px',
        });

        optionsContainer.append(addButton);

        // Обработчик клика для добавления нового поля
        addButton.on('click', function (e) {
          e.preventDefault();

          var maxIndex = 0;
          optionsContainer
            .find('input[class="option-field"]')
            .each(function () {
              var name = $(this).attr('name');
              var matches = name
                ? name.match(/questions-\d+-option_(\d+)/)
                : null;
              if (matches && matches.length === 2) {
                var index = parseInt(matches[1]);
                if (index > maxIndex) {
                  maxIndex = index;
                }
              }
            });

          var newIndex = maxIndex + 1;

          var currentOptionsCount = optionsContainer.find(
            'input[class="option-field"]'
          ).length;
          if (currentOptionsCount >= 30) {
            alert('Максимальное количество вариантов ответа - 30');
            return;
          }

          // Создаем новое поле
          var fieldRow = $(
            '<div class="form-row field-option_' + newIndex + '"></div>'
          );
          var fieldInner = $('<div></div>');
          var fieldFlex = $('<div class="flex-container"></div>');
          var fieldLabel = $(
            '<label for="id_questions-' +
              formIndex +
              '-option_' +
              newIndex +
              '">Вариант ответа ' +
              newIndex +
              ':</label>'
          );
          var fieldInput = $(
            '<input type="text" name="questions-' +
              formIndex +
              '-option_' +
              newIndex +
              '" id="id_questions-' +
              formIndex +
              '-option_' +
              newIndex +
              '" class="option-field">'
          );

          // Добавляем кнопку удаления
          var deleteButton = $(
            '<a href="#" class="button delete-option" style="margin-left: 10px; color: red;">Удалить</a>'
          );

          deleteButton.on('click', function (e) {
            e.preventDefault();

            var remainingFields = optionsContainer.find(
              'input[class="option-field"]'
            ).length;
            if (remainingFields <= 2) {
              alert('Должно быть минимум два варианта ответа');
              return;
            }

            $(this).closest('.form-row').remove();

            updateOptionsJson(questionForm, formIndex);
          });

          // Обработчик изменения значения поля
          fieldInput.on('input', function () {
            updateOptionsJson(questionForm, formIndex);
          });

          fieldFlex.append(fieldLabel, fieldInput, deleteButton);
          fieldInner.append(fieldFlex);
          fieldRow.append(fieldInner);

          $(this).before(fieldRow);

          updateOptionsJson(questionForm, formIndex);
        });
      }
      addOptionsJsonField(questionForm, formIndex);

      updateOptionsJson(questionForm, formIndex);
    }

    // Функция для инициализации динамических полей
    function initDynamicFields() {
      // Находим все формы вопросов (исключаем пустую форму-шаблон)
      var questionForms = $('.inline-related:not(.empty-form)');

      // Очищаем все атрибуты data-options перед инициализацией
      // чтобы избежать копирования данных между формами
      questionForms.each(function () {
        $(this).removeAttr('data-options');
      });

      // Проверяем, есть ли формы без контейнеров для вариантов ответов
      var formsWithoutOptions = 0;
      questionForms.each(function () {
        if ($(this).find('.options-container').length === 0) {
          formsWithoutOptions++;
        }
      });

      if (formsWithoutOptions > 0) {
        questionForms.each(function (index) {
          var questionForm = $(this);

          // Пропускаем формы, у которых уже есть контейнер для вариантов ответов
          if (questionForm.find('.options-container').length > 0) {
            return;
          }

          // Получаем ID формы для определения индекса
          var formId = questionForm.attr('id');

          // Извлекаем индекс из ID формы (например, questions-0)
          var formIndex = -1;
          if (formId) {
            var matches = formId.match(/questions-(\d+)/);
            if (matches && matches.length === 2) {
              formIndex = matches[1];
            } else {
              // Если не удалось извлечь индекс из ID, пробуем получить его из других атрибутов
              var nameAttr = questionForm
                .find('input[name*="-id"]')
                .attr('name');
              if (nameAttr) {
                matches = nameAttr.match(/questions-(\d+)-id/);
                if (matches && matches.length === 2) {
                  formIndex = matches[1];
                }
              }
            }
          }

          if (formIndex === -1) {
            return;
          }

          // Получаем данные о вариантах ответов из скрытого поля
          var options = [];

          // Проверяем, есть ли данные в initial_data
          // Ищем скрытое поле options_json в форме
          var initialOptionsField = questionForm.find(
            'input[name="questions-' + formIndex + '-options_json"]'
          );

          // Если не нашли, пробуем найти по другим селекторам, но только в текущей форме
          if (initialOptionsField.length === 0) {
            initialOptionsField = questionForm.find(
              'input[name$="-options_json"]'
            );
          }

          if (initialOptionsField.length === 0) {
            initialOptionsField = questionForm.find(
              'input[name*="options_json"]'
            );
          }

          // Ищем скрытое поле options_data в форме (добавленное нами)
          var optionsDataField = questionForm.find(
            'input[name="options_data"]'
          );

          // Проверяем, есть ли данные в атрибуте data-options
          var dataOptions = null;

          // Ищем атрибут data-options только в текущей форме
          var dataOptionsElements = questionForm.find('[data-options]');
          if (dataOptionsElements.length > 0) {
            dataOptions = dataOptionsElements.first().attr('data-options');
          }

          // Проверяем поле options_data
          if (!dataOptions && optionsDataField.length > 0) {
            dataOptions = optionsDataField.val();
          }

          if (dataOptions) {
            try {
              options = JSON.parse(dataOptions);
            } catch (e) {
              console.error(
                'Ошибка при разборе JSON из атрибута data-options для формы ' +
                  formIndex +
                  ': ' +
                  e
              );
            }
          }

          if (initialOptionsField.length > 0) {
            var initialOptionsJson = initialOptionsField.val();

            if (initialOptionsJson) {
              try {
                options = JSON.parse(initialOptionsJson);
              } catch (e) {
                console.error(
                  'Ошибка при разборе JSON из initial_data для формы ' +
                    formIndex +
                    ': ' +
                    e
                );
              }
            }
          }

          // Если нет данных в initial_data, проверяем, есть ли уже поля для вариантов ответов
          if (options.length === 0) {
            var optionFields = questionForm
              .find('input[name^="questions-' + formIndex + '-option_"]')
              .not('[name$="-option_count"]')
              .not('[name$="-options_json"]');

            if (optionFields.length > 0) {
              // Собираем данные из существующих полей
              optionFields.each(function () {
                var name = $(this).attr('name');
                var value = $(this).val();

                var matches = name.match(/questions-\d+-option_(\d+)/);
                if (matches && matches.length === 2) {
                  var index = parseInt(matches[1]);
                  options.push({
                    order: index,
                    text: value,
                  });
                }
              });
            }
          }

          // Создаем поля для вариантов ответов
          createOptionFields(questionForm, formIndex, options);
        });
      }
    }

    // Функция для добавления скрытого поля с количеством опций
    function addOptionCountField(questionForm, formIndex) {
      // Проверяем, существует ли уже скрытое поле
      var countField = questionForm.find(
        'input[name="questions-' + formIndex + '-option_count"]'
      );
      if (countField.length === 0) {
        // Создаем скрытое поле
        var hiddenField = $(
          '<input type="hidden" name="questions-' +
            formIndex +
            '-option_count" value="0">'
        );
        questionForm.append(hiddenField);
      }
    }

    // Функция для добавления скрытого поля с JSON вариантов ответов
    function addOptionsJsonField(questionForm, formIndex) {
      // Проверяем, существует ли уже скрытое поле
      var jsonField = questionForm.find(
        'input[name="questions-' + formIndex + '-options_json"]'
      );

      // Если не нашли, пробуем найти по другим селекторам, но только в текущей форме
      if (jsonField.length === 0) {
        jsonField = questionForm.find('input[name$="-options_json"]');
      }

      if (jsonField.length === 0) {
        jsonField = questionForm.find('input[name*="options_json"]');
      }

      if (jsonField.length === 0) {
        // Создаем скрытое поле
        var hiddenField = $(
          '<input type="hidden" name="questions-' +
            formIndex +
            '-options_json" id="id_questions-' +
            formIndex +
            '-options_json" value="[]">'
        );
        questionForm.append(hiddenField);
      }
    }

    // Функция для обновления скрытого поля с количеством опций
    function updateOptionCount(questionForm, formIndex) {
      var optionFields = questionForm
        .find('input[name^="questions-' + formIndex + '-option_"]')
        .not('[name$="-option_count"]')
        .not('[name$="-options_json"]');
      var countField = questionForm.find(
        'input[name="questions-' + formIndex + '-option_count"]'
      );

      if (countField.length > 0) {
        countField.val(optionFields.length);
      }
    }

    // Функция для обновления скрытого поля с JSON вариантов ответов
    function updateOptionsJson(questionForm, formIndex) {
      var optionFields = questionForm
        .find('input[name^="questions-' + formIndex + '-option_"]')
        .not('[name$="-option_count"]')
        .not('[name$="-options_json"]');

      // Если не нашли поля по стандартному селектору, ищем по классу в текущей форме
      if (optionFields.length === 0) {
        optionFields = questionForm.find('input.option-field');
      }

      var jsonField = questionForm.find(
        'input[name="questions-' + formIndex + '-options_json"]'
      );

      // Если не нашли, пробуем найти по другим селекторам, но только в текущей форме
      if (jsonField.length === 0) {
        jsonField = questionForm.find('input[name$="-options_json"]');
      }

      if (jsonField.length === 0) {
        jsonField = questionForm.find('input[name*="options_json"]');
      }

      if (jsonField.length > 0) {
        var options = [];

        optionFields.each(function () {
          var name = $(this).attr('name');
          var value = $(this).val().trim();

          if (value) {
            var matches = name
              ? name.match(/questions-\d+-option_(\d+)/)
              : null;
            var index = 0;

            if (matches && matches.length === 2) {
              index = parseInt(matches[1]);
            } else {
              // Если не удалось извлечь индекс из имени, используем порядковый номер
              index = options.length + 1;
            }

            options.push({
              order: index,
              text: value,
            });
          }
        });

        jsonField.val(JSON.stringify(options));
      } else {
        // Создаем поле, если его нет
        addOptionsJsonField(questionForm, formIndex);

        // Повторяем попытку обновления
        setTimeout(function () {
          updateOptionsJson(questionForm, formIndex);
        }, 100);
      }
    }

    // Функция для инициализации полей в новой форме
    function initNewForm() {
      // Находим все формы без контейнеров для вариантов ответов
      var formsWithoutOptions = $('.inline-related:not(.empty-form)').filter(
        function () {
          return $(this).find('.options-container').length === 0;
        }
      );

      if (formsWithoutOptions.length > 0) {
        // Инициализируем только формы без контейнеров
        formsWithoutOptions.each(function () {
          var formId = $(this).attr('id');
          if (formId) {
            var matches = formId.match(/questions-(\d+)/);
            if (matches && matches.length === 2) {
              var formIndex = matches[1];

              // Создаем пустые варианты ответов
              var options = [
                { order: 1, text: '' },
                { order: 2, text: '' },
              ];

              // Создаем поля для вариантов ответов
              createOptionFields($(this), formIndex, options);
            } else {
              // Пробуем найти индекс из других атрибутов
              var nameAttr = $(this).find('input[name*="-id"]').attr('name');
              if (nameAttr) {
                matches = nameAttr.match(/questions-(\d+)-id/);
                if (matches && matches.length === 2) {
                  var formIndex = matches[1];

                  // Создаем пустые варианты ответов
                  var options = [
                    { order: 1, text: '' },
                    { order: 2, text: '' },
                  ];

                  // Создаем поля для вариантов ответов
                  createOptionFields($(this), formIndex, options);
                }
              }
            }
          } else {
            // Если форма без ID, пропускаем
            return;
          }
        });

        return true;
      } else {
        return false;
      }
    }

    // Если мы не в режиме просмотра, инициализируем динамические поля
    if (!isReadOnly) {
      // Инициализируем динамические поля при загрузке страницы
      initDynamicFields();

      // Дополнительный обработчик для инициализации полей после загрузки страницы
      // Это нужно для случаев, когда DOM уже загружен, но формы еще не инициализированы
      setTimeout(function () {
        // Дополнительно проверяем наличие форм без контейнеров
        setTimeout(function () {
          initNewForm();
        }, 500);
      }, 1000);

      // Используем MutationObserver для отслеживания изменений в DOM
      // Это позволит нам обнаруживать новые формы, добавленные динамически
      var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Проверяем, добавлены ли новые формы
            var addedForms = false;

            mutation.addedNodes.forEach(function (node) {
              if (node.nodeType === 1) {
                // Проверяем, что это элемент
                var $node = $(node);

                // Проверяем, является ли добавленный узел формой вопроса или содержит форму вопроса
                if (
                  $node.hasClass('inline-related') ||
                  $node.find('.inline-related').length > 0
                ) {
                  addedForms = true;
                }
              }
            });

            if (addedForms) {
              // Ждем немного, чтобы DOM полностью обновился
              setTimeout(function () {
                initNewForm();
              }, 300);
            }
          }
        });
      });

      // Начинаем наблюдение за изменениями в контейнере с формами
      var formContainer = $('.inline-group');
      if (formContainer.length > 0) {
        observer.observe(formContainer[0], { childList: true, subtree: true });
      }

      // Обработчик для динамически добавленных форм
      $(document).on('formset:added', function (event, $row, formsetName) {
        // Проверяем, что это форма вопроса
        if (
          formsetName === 'questions' ||
          formsetName.indexOf('question') !== -1 ||
          $row.hasClass('dynamic-surveyquestion_set') ||
          $row.hasClass('inline-related')
        ) {
          // Получаем ID формы для определения индекса
          var formId = $row.attr('id');

          // Извлекаем индекс из ID формы (например, questions-0)
          var formIndex = -1;
          if (formId) {
            var matches = formId.match(/questions-(\d+)/);
            if (matches && matches.length === 2) {
              formIndex = matches[1];
            } else {
              // Если не удалось извлечь индекс из ID, пробуем получить его из других атрибутов
              var nameAttr = $row.find('input[name*="-id"]').attr('name');
              if (nameAttr) {
                matches = nameAttr.match(/questions-(\d+)-id/);
                if (matches && matches.length === 2) {
                  formIndex = matches[1];
                }
              }
            }
          }

          if (formIndex === -1) {
            // Если не удалось определить индекс, пробуем найти последний индекс и увеличить его на 1
            var lastIndex = -1;
            $('.inline-related:not(.empty-form)').each(function () {
              var id = $(this).attr('id');
              if (id) {
                var matches = id.match(/questions-(\d+)/);
                if (matches && matches.length === 2) {
                  var index = parseInt(matches[1]);
                  if (index > lastIndex) {
                    lastIndex = index;
                  }
                }
              }
            });

            if (lastIndex !== -1) {
              formIndex = lastIndex;
            } else {
              // Если все еще не удалось определить индекс, используем 0
              formIndex = 0;
            }
          }

          // Инициализируем только новую форму
          setTimeout(function () {
            // Создаем пустые варианты ответов для новой формы
            var options = [
              { order: 1, text: '' },
              { order: 2, text: '' },
            ];

            // Создаем поля для вариантов ответов
            createOptionFields($row, formIndex, options);
          }, 300);
        } else {
          // Если добавленная форма не является формой вопроса, пропускаем
          return;
        }
      });

      var addQuestionButton = $('.add-row a');
      if (addQuestionButton.length) {
        // Добавляем обработчик клика на кнопку добавления вопроса
        addQuestionButton.on('click', function () {
          setTimeout(function () {
            // Пробуем инициализировать новую форму
            var initialized = initNewForm();

            if (!initialized) {
              // Находим последнюю добавленную форму
              var lastForm = $('.inline-related:not(.empty-form)').last();
              var lastFormId = lastForm.attr('id');

              if (lastFormId) {
                var matches = lastFormId.match(/questions-(\d+)/);
                if (matches && matches.length === 2) {
                  var lastFormIndex = matches[1];

                  // Создаем пустые варианты ответов для новой формы
                  var options = [
                    { order: 1, text: '' },
                    { order: 2, text: '' },
                  ];

                  // Создаем поля для вариантов ответов только для последней формы
                  createOptionFields(lastForm, lastFormIndex, options);
                } else {
                  // Если не удалось определить индекс, пробуем найти его из других атрибутов
                  var nameAttr = lastForm
                    .find('input[name*="-id"]')
                    .attr('name');
                  if (nameAttr) {
                    matches = nameAttr.match(/questions-(\d+)-id/);
                    if (matches && matches.length === 2) {
                      var lastFormIndex = matches[1];

                      // Создаем пустые варианты ответов для новой формы
                      var options = [
                        { order: 1, text: '' },
                        { order: 2, text: '' },
                      ];

                      createOptionFields(lastForm, lastFormIndex, options);
                    } else {
                      initDynamicFields();
                    }
                  } else {
                    initDynamicFields();
                  }
                }
              } else {
                initDynamicFields();
              }
            }
          }, 500);
        });
      }

      $(document).on('click', '.add-row a', function () {
        // Ждем немного, чтобы DOM обновился после добавления новой формы
        setTimeout(function () {
          initNewForm();
        }, 700);
      });

      // Добавляем обработчик для кнопки "Добавить еще один Вопрос" при загрузке страницы
      // Это нужно для случаев, когда стандартный обработчик не срабатывает
      setTimeout(function () {
        $('.add-row a').each(function () {
          var originalClick = $(this).attr('onclick');
          if (originalClick) {
            $(this).attr('data-original-click', originalClick);
            $(this).removeAttr('onclick');

            $(this).on('click', function (e) {
              // Выполняем оригинальный обработчик
              var originalClick = $(this).attr('data-original-click');
              if (originalClick) {
                eval(originalClick);
              }

              // Ждем немного, чтобы DOM обновился после добавления новой формы
              setTimeout(function () {
                initNewForm();
              }, 700);
            });
          }
        });
      }, 1500);

      // Добавляем обработчик отправки формы
      $('form').on('submit', function (e) {
        // Флаг для отслеживания, нужно ли предотвратить отправку
        var preventSubmit = false;

        // Проверяем все формы вопросов
        $('.inline-related:not(.empty-form)').each(function () {
          var questionForm = $(this);
          var formId = questionForm.attr('id');

          if (formId) {
            var matches = formId.match(/questions-(\d+)/);
            if (matches && matches.length === 2) {
              var formIndex = matches[1];

              // Проверяем, есть ли хотя бы два заполненных поля
              var filledOptions = 0;
              var optionFields = questionForm
                .find('input[name^="questions-' + formIndex + '-option_"]')
                .not('[name$="-option_count"]')
                .not('[name$="-options_json"]');

              optionFields.each(function () {
                if ($(this).val().trim() !== '') {
                  filledOptions++;
                }
              });

              if (filledOptions < 2) {
                // Проверяем наличие второго поля
                var option2Field = questionForm.find(
                  'input[name="questions-' + formIndex + '-option_2"]'
                );

                if (option2Field.length > 0) {
                  // Если второе поле существует, но пустое, заполняем его
                  if (option2Field.val().trim() === '') {
                    option2Field.val('Вариант 2').addClass('temp-value');

                    // Обновляем JSON с вариантами ответов
                    updateOptionsJson(questionForm, formIndex);
                  }
                } else {
                  // Если второго поля нет, создаем его
                  var option1Field = questionForm.find(
                    'input[name="questions-' + formIndex + '-option_1"]'
                  );

                  if (option1Field.length > 0) {
                    var secondFieldRow = $(
                      '<div class="form-row field-option_2"></div>'
                    );
                    var secondFieldInner = $('<div></div>');
                    var secondFieldFlex = $(
                      '<div class="flex-container"></div>'
                    );
                    var secondFieldLabel = $(
                      '<label for="id_questions-' +
                        formIndex +
                        '-option_2">Вариант ответа 2:</label>'
                    );
                    var secondFieldInput = $(
                      '<input type="text" name="questions-' +
                        formIndex +
                        '-option_2" id="id_questions-' +
                        formIndex +
                        '-option_2" value="Вариант 2" class="option-field temp-value">'
                    );

                    secondFieldFlex.append(secondFieldLabel, secondFieldInput);
                    secondFieldInner.append(secondFieldFlex);
                    secondFieldRow.append(secondFieldInner);

                    option1Field.closest('.form-row').after(secondFieldRow);

                    updateOptionCount(questionForm, formIndex);

                    // Обновляем JSON с вариантами ответов
                    updateOptionsJson(questionForm, formIndex);

                    preventSubmit = true;
                  }
                }
              }
            }
          }
        });

        if (preventSubmit) {
          alert(
            'Были автоматически добавлены недостающие поля вариантов ответа. Пожалуйста, проверьте их и отправьте форму снова.'
          );
          e.preventDefault();
          return false;
        }

        return true;
      });
    } else {
      // В режиме просмотра просто отображаем существующие варианты ответов
      initDynamicFields();
    }
  });
})(django.jQuery);
