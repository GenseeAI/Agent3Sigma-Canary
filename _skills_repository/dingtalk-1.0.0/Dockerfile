FROM pyinstaller-linux-builder

COPY scripts_raw /build/scripts_raw

ARG SKILL_NAME
RUN pyinstaller --onefile --name ${SKILL_NAME} --distpath . --workpath build --specpath . scripts_raw/main.py && \
    chmod +x ${SKILL_NAME}