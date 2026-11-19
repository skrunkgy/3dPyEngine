#version 330 core

in vec2 texCoord;

uniform sampler2D billTex;

out vec4 fragColor;

void main() {
    fragColor = texture(billTex, texCoord);
    if (fragColor.a < .1) {
        discard;
    } 
}