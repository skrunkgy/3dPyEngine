#version 330

uniform sampler2D gui;
in vec2 texCoord;
out vec4 FragColor;

void main() {
    FragColor = texture(gui, texCoord);
    if (FragColor.a < 0.01) {
        discard;
    }
}