# V3-Advanced Query-only Replay Summary

- runDate: 2026-02-24
- maxSamples: 200

## Q16
- sampleSize: 200
- statusCoverageRdbBaseline: `{"ANSWERED":192,"SPOILER_BLOCKED":8}`
- metrics: `{"statusExactMatchRate":1.0,"anchorExactMatchRate":1.0,"contextExactMatchRate":1.0,"evidenceJaccardAvg":1.0}`
- passChecks: `{"sampleSizeAtLeast500":false,"statusExactMatchAtLeast99_5pct":true,"anchorExactMatchAtLeast99_0pct":true,"contextExactMatchAtLeast99_0pct":true,"evidenceJaccardAvgAtLeast0_85":true}`

## Q17
- sampleSize: 50
- statusCoverageRdbBaseline: `{"NOT_ENOUGH_DATA":48,"SPOILER_BLOCKED":2}`
- metrics: `{"candidateCapOverflowRate":0.0,"normalStatusExactMatchRate":1.0,"normalEvidenceJaccardAvg":1.0,"capOverflowStatusParityRefRate":null}`
- passChecks: `{"sampleSizeAtLeast500":false,"statusCoverageSpoilerBlockedAtLeast30":false,"statusCoverageNotEnoughDataAtLeast30":true,"normalStatusExactMatchAtLeast99_5pct":true,"normalEvidenceJaccardAvgAtLeast0_85":true,"candidateCapOverflowRateAtMost5pct":true}`

## Q19
- sampleSize: 200
- statusCoverageRdbBaseline: `{"ANSWERED":150,"NOT_ENOUGH_DATA":50}`
- metrics: `{"statusExactMatchRate":1.0,"axisExactMatchRate":1.0,"evidenceJaccardAvg":1.0}`
- passChecks: `{"sampleSizeAtLeast500":false,"statusExactMatchAtLeast99_5pct":true,"axisExactMatchAtLeast99_0pct":true,"evidenceJaccardAvgAtLeast0_85":true}`

