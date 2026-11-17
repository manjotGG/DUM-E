# Engine log upload format

Open **Upload engine log** in the sidebar. Download the sample, select a file, then click **Analyze log & predict**. Results give one remaining-life estimate per engine at its latest uploaded observation. Uploading is inference only; it does not train or change the saved model.

Use UTF-8 CSV, TXT, TSV, or LOG files with one observation per row. CSV uses commas; text/TSV uses whitespace. File extensions do not change the required numeric schema. Maximum file size: 10 MiB, maximum observations: 30,000, maximum engines: 200. Files are processed in memory for that request and are not persisted on the server.

Each engine needs **at least 15 consecutive cycles**, the longest window used by the trained feature pipeline. Supply all available history when possible. Cycles can start later than one, but must increase by one within each engine. Engine IDs can be any positive integer; they group rows and are not numerical predictors. The engine/cycle integer limit is 2,147,483,647. Gaps, duplicate cycles, reversed observations, missing values, nonfinite values, and extreme numeric magnitudes are rejected.

Every row must provide these 26 columns:

```text
engine_id,cycle,setting_1,setting_2,setting_3,T2,T24,T30,T50,P2,P15,P30,Nf,Nc,epr,Ps30,phi,NRf,NRc,BPR,farB,htBleed,Nf_dmd,PCNfR_dmd,W31,W32
```

Headered CSV/TSV files may use `sensor_1` through `sensor_21` instead of the corresponding measurement symbols, and can reorder columns. Headerless files must follow the order above. The built-in engine CSV download also uses an accepted schema. Headers are matched without case sensitivity. Extra columns, including RUL labels, must be removed before uploading.

Sensor descriptions and original units follow **Table 2 of [NASA’s Damage Propagation Modeling for Aircraft Engine Prognostics](https://ntrs.nasa.gov/api/citations/20090029214/downloads/20090029214.pdf)**. The shared dictionary is `shared/sensors.json`; display names do not change the internal keys used by the trained model. HPC/LPC mean high/low-pressure compressor; HPT/LPT mean high/low-pressure turbine. °R denotes degrees Rankine, psia denotes absolute pressure in pounds per square inch, and rpm denotes revolutions per minute. Bleed enthalpy has no physical unit specified in the published table; the UI retains “dataset units” without inventing a conversion.

The sample download contains the 31 supplied observations for FD001 test engine 1, with named sensor headers. It is useful for checking the flow before preparing a custom log. It is not newly generated telemetry. NASA C-MAPSS contains simulation-generated degradation data.

The estimator was validated on **FD001 only**: one operating condition and HPC degradation. A file matching the schema does not establish that different equipment or regimes are supported. Keep sensor values in the original units and do not normalize them yourself—the saved pipeline handles its fitted transformations. Logs do not include failure labels, so upload results are estimates rather than measured accuracy reports. The Model performance page uses the original official test labels, independently of uploads.

For logs longer than 500 cycles per engine, the chart shows the last 500 observations for responsiveness. Inference uses the uploaded history, including the current absolute cycle and the required trailing windows. The result reports the full observation count and first/latest cycles. Selecting another file clears the previous result; completed analysis remains available when navigating away and back during the browser session, and is cleared on refresh.

The endpoint is `POST /api/engines/analyze-log` with the raw file bytes as the body (`Content-Type: application/octet-stream`). It returns 422 for invalid logs, 413 for the size limit, and 503 if the model is unavailable. The schema and sample are available at `/api/engines/log-schema` and `/api/engines/sample-log`.
