#version 330 core
in vec3 position;
in float life;
in vec3 color;
in float angle;              // kat obrotu lezki (z kierunku lotu)
in float psize;             // mnoznik rozmiaru kropli (glowne=1, rozbryzg<1)
out float v_life;
out vec3 v_color;
out float v_angle;
uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform float point_scale;
void main() {
    v_life = life;
    v_color = color;
    v_angle = angle;
    vec4 view_pos = view_matrix * vec4(position, 1.0);
    float dist = length(view_pos.xyz);
    gl_Position = projection_matrix * view_pos;
    gl_PointSize = point_scale * psize / dist;
}
