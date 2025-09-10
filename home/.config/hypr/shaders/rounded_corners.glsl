#version 300 es
precision highp float;

in vec2 v_texcoord;
out vec4 fragColor;

uniform sampler2D tex;

// Параметры
#ifndef CORNER_RADIUS_PX
#define CORNER_RADIUS_PX 20.0
#endif

#ifndef CORNER_SMOOTH_PX
#define CORNER_SMOOTH_PX 1.0   // 1.0–1.5 обычно достаточно
#endif

#ifndef CORNER_COLOR
#define CORNER_COLOR vec4(0.0, 0.0, 0.0, 1.0) // цвет угла (вне скруглённого прямоугольника)
#endif

#ifndef CORNER_INSET_PX
#define CORNER_INSET_PX 0.5    // полпикселя для выравнивания кромки по сетке
#endif

// SDF скруглённого прямоугольника (центр в (0,0))
float sdRoundedBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - (b * 0.5 - vec2(r));
    return length(max(q, 0.0)) - r;
}

void main() {
    vec2 res = vec2(textureSize(tex, 0));

    // Координата текущего пикселя (центр пикселя)
    vec2 pix = gl_FragCoord.xy - 0.5;

    // Центруем систему координат
    vec2 p = pix - 0.5 * (res - 1.0);

    // Лёгкий "инсет" размеров и радиуса для пиксель-идеального края
    float radius = max(0.0, CORNER_RADIUS_PX - CORNER_INSET_PX);
    vec2 dims    = max(res - vec2(2.0 * CORNER_INSET_PX), vec2(1.0));

    // Расстояние до границы скруглённого прямоугольника (в пикселях)
    float d = sdRoundedBox(p, dims, radius);

    // Антиалиас: ширина из градиента расстояния (в пикселях)
    float grad = length(vec2(dFdx(d), dFdy(d))) + 1e-6;
    float aa = max(grad, 1.0) * CORNER_SMOOTH_PX;

    // Симметричное сглаживание вокруг нуля устраняет "клин" в месте стыка
    float mask = 1.0 - smoothstep(-aa, aa, d);

    vec4 src = texture(tex, v_texcoord);
    fragColor = mix(CORNER_COLOR, src, mask);
}