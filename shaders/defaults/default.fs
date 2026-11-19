#version 330 core

in VS_OUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} fs_in;

#define MAX_LIGHT_COUNT 16
struct Light {
    vec3 position;
    vec3 color;
    float intensity;
    bool enabled;
};

uniform Light lights[MAX_LIGHT_COUNT];
uniform sampler2D texture1;

out vec4 color;

void main() {

    vec3 lighting;

    for (int i = 0; i < MAX_LIGHT_COUNT; i++) {

        if (!lights[i].enabled) {
            continue;
        }

        vec3 lightDir = normalize(lights[i].position - fs_in.position);
        float diffuse = max(dot(fs_in.normal, lightDir), 0);

        lighting += lights[i].color * diffuse * (lights[i].intensity); // pow(distance(fs_in.position.xyz, lights[i].position.xyz), 2));
    }

    color = vec4(lighting, 1.0) * texture(texture1, fs_in.uv);
    
}

vec3 calcLight() {
    return vec3(0.0, 0.0, 0.0);
}