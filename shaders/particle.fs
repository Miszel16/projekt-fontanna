#version 330 core
in float v_life;
in vec3 v_color;
out vec4 frag_color;
uniform sampler2D sprite;
void main() {
    if (v_life <= 0.0) discard;               // martwe czastki niewidoczne
    vec4 tex = texture(sprite, gl_PointCoord);

    // Kolor kropli z palety. Krycie wprost z tekstury (miekki brzeg = lekkie
    // rozmycie). Niski prog odciecia, zeby delikatny brzeg pozostal widoczny.
    float alpha = tex.a;
    if (alpha < 0.05) discard;
    frag_color = vec4(v_color, alpha);
}