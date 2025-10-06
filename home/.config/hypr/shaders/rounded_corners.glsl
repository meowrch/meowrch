#version 300 es
precision mediump float;

in vec2 v_texcoord;
out vec4 fragColor;

uniform sampler2D tex;

#ifndef CORNER_RADIUS_PX
#define CORNER_RADIUS_PX 20.0
#endif
#ifndef CORNER_SMOOTH_PX
#define CORNER_SMOOTH_PX 1.0
#endif
#ifndef CORNER_INSET_PX
#define CORNER_INSET_PX 0.0
#endif

// Переключатель качества AA: 0 = быстрый (без fwidth), 1 = качественный (с fwidth)
#ifndef AA_QUALITY
#define AA_QUALITY 1
#endif

float sdRoundedBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - (b * 0.5 - vec2(r));
    return length(max(q, 0.0)) - r;
}

void main() {
    vec2 res  = vec2(textureSize(tex, 0));
    vec2 p    = (v_texcoord - 0.5) * res;

    float radius = max(0.0, CORNER_RADIUS_PX - CORNER_INSET_PX);
    vec2  dims   = max(res - vec2(2.0 * CORNER_INSET_PX), vec2(1.0));

    float d = sdRoundedBox(p, dims, radius);

#if AA_QUALITY == 1
    // Качественный AA
    float aa = max(fwidth(d), 1e-6) * CORNER_SMOOTH_PX;
    float mask = 1.0 - smoothstep(-aa, aa, d);
#else
    // Быстрый AA с константной шириной
    float aa = max(CORNER_SMOOTH_PX, 1e-6);
    // Линейная аппроксимация вместо smoothstep — чуть резче, но быстрее
    float mask = clamp(0.5 - 0.5 * d / aa, 0.0, 1.0);
#endif

    // Ранние выходы
    if (mask <= 0.0) {
        fragColor = vec4(0.0);
        return;
    }

    vec4 src = texture(tex, v_texcoord);

    if (mask >= 1.0) {
        fragColor = src;       // полностью внутри — без умножения
    } else {
        fragColor = src * mask; // premultiplied
    }
}
