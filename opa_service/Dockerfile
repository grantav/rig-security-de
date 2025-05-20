FROM openpolicyagent/opa:latest
COPY policy.rego /policies/policy.rego
EXPOSE 8181
CMD ["run", "--server", "--watch", "/policies"]
