{{/*
Generate the fullname for resources.
*/}}
{{- define "hackathon-todo.fullname" -}}
{{- default .Chart.Name .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels for all resources.
*/}}
{{- define "hackathon-todo.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels helper — takes an app name as argument.
Usage: {{ include "hackathon-todo.selectorLabels" (dict "app" "backend") }}
*/}}
{{- define "hackathon-todo.selectorLabels" -}}
app: {{ .app }}
{{- end }}
