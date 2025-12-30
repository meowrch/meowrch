#version 330 core

// Атрибуты вершин (координаты текстуры), передаются из вершинного шейдера
in vec2 v_texcoord;

// Выходной цвет фрагмента (пикселя)
out vec4 fragColor;

// Текстура экрана, которую мы будем обрабатывать
uniform sampler2D tex;

void main() {
    // Получаем цвет пикселя из текстуры экрана по его координатам
    vec4 original_color = texture(tex, v_texcoord);

    // Вычисляем расстояние от текущего пикселя до центра экрана (координаты 0.5, 0.5)
    float distance_to_center = distance(v_texcoord, vec2(0.5));

    // Чем дальше пиксель от центра, тем он будет темнее. 
    // Множитель 0.7 контролирует интенсивность затемнения.
    float darkening_factor = 1.0 - distance_to_center * 0.7;

    // Применяем затемнение к оригинальному цвету и выводим результат
    fragColor = vec4(original_color.rgb * darkening_factor, original_color.a);
}

