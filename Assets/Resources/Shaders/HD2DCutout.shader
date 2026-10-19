// Pixel art opaca com recorte de transparência (chão, paredes, objetos, personagens).
// Iluminação vem pronta de fora (_Color) + névoa de distância global.
Shader "Joaquim/HD2D/Cutout"
{
    Properties
    {
        _MainTex ("Textura", 2D) = "white" {}
        _Color ("Tom (luz da cena)", Color) = (1,1,1,1)
        _Cutoff ("Recorte", Range(0,1)) = 0.5
        _Flip ("Espelhar", Float) = 0
        _NoHaze ("Sem névoa", Float) = 0
    }
    SubShader
    {
        Tags { "Queue"="AlphaTest" "RenderType"="TransparentCutout" "IgnoreProjector"="True" }
        Cull Off

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            fixed4 _Color;
            float _Cutoff;
            float _Flip;
            float _NoHaze;
            float4 _HazeColor;     // global
            float _HazeDensity;    // global
            float _HazeStrength;   // global

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float haze : TEXCOORD1;
            };

            v2f vert (appdata_base v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                float2 uv = v.texcoord.xy;
                uv.x = lerp(uv.x, 1.0 - uv.x, _Flip);
                o.uv = uv;
                float3 wp = mul(unity_ObjectToWorld, v.vertex).xyz;
                float dist = distance(wp, _WorldSpaceCameraPos);
                o.haze = (1.0 - exp(-dist * _HazeDensity)) * _HazeStrength * (1.0 - _NoHaze);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 t = tex2D(_MainTex, i.uv);
                clip(t.a - _Cutoff);
                fixed3 c = t.rgb * _Color.rgb;
                c = lerp(c, _HazeColor.rgb, saturate(i.haze));
                return fixed4(c, 1);
            }
            ENDCG
        }

        // Usado pela Unity para preencher o _CameraDepthTexture (profundidade → desfoque)
        Pass
        {
            Tags { "LightMode"="ShadowCaster" }
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_shadowcaster
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float _Cutoff;
            float _Flip;

            struct v2f
            {
                V2F_SHADOW_CASTER;
                float2 uv : TEXCOORD1;
            };

            v2f vert (appdata_base v)
            {
                v2f o;
                TRANSFER_SHADOW_CASTER_NORMALOFFSET(o)
                float2 uv = v.texcoord.xy;
                uv.x = lerp(uv.x, 1.0 - uv.x, _Flip);
                o.uv = uv;
                return o;
            }

            float4 frag (v2f i) : SV_Target
            {
                clip(tex2D(_MainTex, i.uv).a - _Cutoff);
                SHADOW_CASTER_FRAGMENT(i)
            }
            ENDCG
        }
    }
}
