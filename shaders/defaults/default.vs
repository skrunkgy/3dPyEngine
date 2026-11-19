#version 330 core

layout (location = 0) in vec3 positions;
layout (location = 1) in vec2 uvcoords;
layout (location = 2) in vec3 normals;

uniform mat4x4 projectionM;
uniform mat4x4 viewM;
uniform mat4x4 modelM;

out VS_OUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} vs_out;

void main() {
    vs_out.position =  vec3(modelM * vec4(positions, 1));
    vs_out.uv = uvcoords;
    vs_out.normal = normals;
    gl_Position = projectionM * viewM * modelM * vec4(positions, 1.0);
}