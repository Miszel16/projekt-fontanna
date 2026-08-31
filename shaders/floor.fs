#version 330 core
in vec2 v_uv;
out vec4 frag_color;
uniform sampler2D floor_texture;
void main() {
    frag_color = texture(floor_texture, v_uv);
}
