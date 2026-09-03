#version 330 core
in float v_life;
in vec3 v_color;
in float v_angle;
out vec4 frag_color;
uniform sampler2D sprite;
void main() {
    if (v_life <= 0.0) discard;               // martwe czastki niewidoczne

    // Obrot wspolrzednych tekstury wokol srodka punktu o kat v_angle.
    // Dzieki temu teksturowany point-sprite (lezka) "obraca sie" zgodnie
    // z kierunkiem lotu, mimo ze sam punkt jest zawsze zwrocony do kamery.
    vec2 uv = gl_PointCoord - vec2(0.5);
    float s = sin(v_angle);
    float c = cos(v_angle);
    uv = vec2(c * uv.x - s * uv.y, s * uv.x + c * uv.y);
    uv += vec2(0.5);

    vec4 tex = texture(sprite, uv);

    // Kolor kropli z palety. Krycie wprost z tekstury (miekki brzeg).
    float alpha = tex.a;
    if (alpha < 0.05) discard;
    frag_color = vec4(v_color, alpha);
}