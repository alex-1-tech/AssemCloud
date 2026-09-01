document.addEventListener('DOMContentLoaded', function () {
    const modelSelect = document.querySelector('#id_model');
    const schemeSelect = document.querySelector('#id_scheme');
    const otherDataField = document.querySelector('#id_other_data');

    if (!modelSelect || !schemeSelect || !otherDataField) return;

    const API_URL = '/admin/core/equipment/get-schemes/';

    const otherDataRow = otherDataField.closest('.form-row') || otherDataField.closest('div');
    if (otherDataRow) otherDataRow.style.display = 'none';

    const container = document.createElement('div');
    container.id = 'scheme-dynamic-fields';
    otherDataRow.insertAdjacentElement('afterend', container);

    function parseExistingData() {
        try {
            return JSON.parse(otherDataField.value || '{}') || {};
        } catch (e) {
            return {};
        }
    }

    function clearContainer() {
        container.innerHTML = '';
    }

    function buildFieldRow(fieldDef, value) {        
        const name = 'json_field_' + fieldDef.name;
        const id = 'id_' + name;
        const isCheckbox = fieldDef.type === 'boolean';

        const row = document.createElement('div');
        row.className = 'form-row field-' + name + (isCheckbox ? ' checkbox-row' : '');

        const innerDiv = document.createElement('div');

        const label = document.createElement('label');
        label.setAttribute('for', id);
        
        // Используем label из схемы, с фоллбеком на name
        const labelText = fieldDef.label || fieldDef.name;
        label.textContent = labelText + (isCheckbox ? '' : ':');

        if (fieldDef.required) label.classList.add('required');
        if (isCheckbox) label.classList.add('vCheckboxLabel');

        const input = buildInput(fieldDef, value, name, id);
        if (isCheckbox) {
            innerDiv.appendChild(input);
            innerDiv.appendChild(label);
        } else {
            innerDiv.appendChild(label);
            innerDiv.appendChild(input);
        }

        row.appendChild(innerDiv);
        return row;
    }

    function buildInput(fieldDef, value, name, id) {
        let input;

        switch (fieldDef.type) {
            case 'boolean':
                input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = Boolean(value ?? fieldDef.default ?? false);
                break;
            case 'text':
                input = document.createElement('textarea');
                input.rows = 3;
                input.className = 'vLargeTextField';
                input.value = value ?? fieldDef.default ?? '';
                break;
            case 'integer':
            case 'int':
                input = document.createElement('input');
                input.type = 'number';
                input.className = 'vIntegerField';
                input.value = value ?? fieldDef.default ?? '';
                break;
            default:
                input = document.createElement('input');
                input.type = 'text';
                input.className = 'vTextField';
                // Автоматическое ограничение длины 255, если не переопределено в схеме
                input.maxLength = fieldDef.max_length || 255;
                input.value = value ?? fieldDef.default ?? '';
        }

        input.name = name;
        input.id = id;
        
        // Значение по умолчанию false для обязательности
        if (fieldDef.required) input.required = true;
        
        return input;
    }

    function renderFields(fieldsDescription, prefillData) {
        clearContainer();
        const sections = (fieldsDescription && fieldsDescription.sections) || [];

        sections.forEach(function (section) {
            const title = section.title || section.key;
            if (title) {
                const heading = document.createElement('h2');
                heading.textContent = title;
                container.appendChild(heading);
            }

            (section.fields || []).forEach(function (fieldDef) {
                container.appendChild(buildFieldRow(fieldDef, prefillData[fieldDef.name]));
            });
        });
    }

    function loadSchemeFields(schemeId) {
        if (!schemeId) {
            clearContainer();
            return;
        }
        fetch(API_URL + '?scheme_id=' + encodeURIComponent(schemeId))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.fields_description) {
                    renderFields(data.fields_description, parseExistingData());
                }
            })
            .catch(function (err) { console.error('Ошибка загрузки полей схемы:', err); });
    }

    function loadSchemesForModel(modelId, selectSchemeId) {
        schemeSelect.innerHTML = '<option value="">---------</option>';
        clearContainer();
        if (!modelId) return;

        fetch(API_URL + '?model_id=' + encodeURIComponent(modelId))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                (data.schemes || []).forEach(function (scheme) {
                    const option = document.createElement('option');
                    option.value = scheme.id;
                    option.textContent = scheme.name;
                    if (String(scheme.id) === String(selectSchemeId)) {
                        option.selected = true;
                    }
                    schemeSelect.appendChild(option);
                });
                if (selectSchemeId) loadSchemeFields(selectSchemeId);
            })
            .catch(function (err) { console.error('Ошибка загрузки списка схем:', err); });
    }

    modelSelect.addEventListener('change', function () {
        loadSchemesForModel(this.value, null);
    });

    schemeSelect.addEventListener('change', function () {
        loadSchemeFields(this.value);
    });

    if (schemeSelect.value) {
        loadSchemeFields(schemeSelect.value);
    }
});