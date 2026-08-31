#version 330 core
in vec3 position;
in vec2 uv;
out vec2 v_uv;
uniform mat4 projection_matrix;
uniform mat4 view_matrix;
void main() {
    v_uv = uv;
    gl_Position = projection_matrix * view_matrix * vec4(position, 1.0);
}
