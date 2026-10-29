import 'dart:convert';
import 'dart:typed_data';
import 'package:test/test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import '../ai_vision/gemini_code/gemini_service.dart';

void main() {
  group('DiagnosisResult Domain Model Tests', () {
    test('Correctly parses valid fault JSON with bounding box', () {
      final jsonMap = {
        'status': 'SUCCESS',
        'fault_detected': true,
        'fault_type': 'DISCONNECTED_WIRE',
        'location': 'Breadboard Row 15 to Switch',
        'possible_cause': 'Jumper wire unseated',
        'confidence': 0.92,
        'bounding_box': {
          'ymin': 0.35,
          'xmin': 0.42,
          'ymax': 0.58,
          'xmax': 0.65,
        }
      };

      final result = DiagnosisResult.fromJson(jsonMap);

      expect(result.status, 'SUCCESS');
      expect(result.faultDetected, true);
      expect(result.faultType, 'DISCONNECTED_WIRE');
      expect(result.location, 'Breadboard Row 15 to Switch');
      expect(result.possibleCause, 'Jumper wire unseated');
      expect(result.confidence, 0.92);
      expect(result.boundingBox, isNotNull);
      expect(result.boundingBox!.ymin, 0.35);
      expect(result.boundingBox!.xmin, 0.42);
      expect(result.boundingBox!.ymax, 0.58);
      expect(result.boundingBox!.xmax, 0.65);
    });

    test('Normalizes 0-1000 integer bounding box coordinates to 0.0-1.0', () {
      final jsonMap = {
        'status': 'SUCCESS',
        'fault_detected': true,
        'fault_type': 'LOOSE_WIRE',
        'location': 'Switch Terminal',
        'possible_cause': 'Loose pin connection',
        'confidence': 0.88,
        'bounding_box': {
          'ymin': 350,
          'xmin': 420,
          'ymax': 580,
          'xmax': 650,
        }
      };

      final result = DiagnosisResult.fromJson(jsonMap);

      expect(result.boundingBox, isNotNull);
      expect(result.boundingBox!.ymin, closeTo(0.35, 0.001));
      expect(result.boundingBox!.xmin, closeTo(0.42, 0.001));
      expect(result.boundingBox!.ymax, closeTo(0.58, 0.001));
      expect(result.boundingBox!.xmax, closeTo(0.65, 0.001));
    });

    test('Clamps confidence values between 0.0 and 1.0', () {
      final jsonMapHigh = {
        'status': 'SUCCESS',
        'fault_detected': false,
        'fault_type': 'NONE',
        'location': 'Loop intact',
        'possible_cause': 'All pins seated',
        'confidence': 1.45,
      };
      final resultHigh = DiagnosisResult.fromJson(jsonMapHigh);
      expect(resultHigh.confidence, 1.0);

      final jsonMapLow = {
        'status': 'SUCCESS',
        'fault_detected': false,
        'fault_type': 'NONE',
        'location': 'Loop intact',
        'possible_cause': 'All pins seated',
        'confidence': -0.5,
      };
      final resultLow = DiagnosisResult.fromJson(jsonMapLow);
      expect(resultLow.confidence, 0.0);
    });

    test('Enforces consistent states for UNKNOWN status', () {
      final jsonMap = {
        'status': 'UNKNOWN',
        'fault_detected': true,
        'fault_type': 'DISCONNECTED_WIRE',
        'location': 'Unknown',
        'possible_cause': 'Blurry image',
        'confidence': 0.0,
      };

      final result = DiagnosisResult.fromJson(jsonMap);

      expect(result.status, 'UNKNOWN');
      expect(result.faultDetected, false);
      expect(result.faultType, 'UNKNOWN');
    });

    test('Serialization toJson reproduces contract map', () {
      final result = DiagnosisResult(
        status: 'SUCCESS',
        faultDetected: true,
        faultType: 'DISCONNECTED_WIRE',
        location: 'Breadboard Pin 5',
        possibleCause: 'Unplugged wire',
        confidence: 0.94,
        boundingBox: const BoundingBox(ymin: 0.1, xmin: 0.2, ymax: 0.3, xmax: 0.4),
      );

      final jsonMap = result.toJson();

      expect(jsonMap['status'], 'SUCCESS');
      expect(jsonMap['fault_detected'], true);
      expect(jsonMap['fault_type'], 'DISCONNECTED_WIRE');
      expect(jsonMap['bounding_box'], isNotNull);
      expect(jsonMap['bounding_box']['ymin'], 0.1);
    });
  });

  group('GeminiService Network & Retry Tests', () {
    test('Returns error when image bytes are empty', () async {
      final service = GeminiService(apiKey: 'dummy_key');
      final result = await service.analyzeCircuitImage(Uint8List(0));

      expect(result.status, 'ERROR');
      expect(result.possibleCause, contains('empty'));
    });

    test('Returns error when API key is missing', () async {
      final service = GeminiService(apiKey: '');
      final result = await service.analyzeCircuitImage(Uint8List.fromList([1, 2, 3]));

      expect(result.status, 'ERROR');
      expect(result.possibleCause, contains('GEMINI_API_KEY'));
    });

    test('Successfully parses HTTP 200 Gemini candidate response', () async {
      final mockResponse = jsonEncode({
        'candidates': [
          {
            'content': {
              'parts': [
                {
                  'text': jsonEncode({
                    'status': 'SUCCESS',
                    'fault_detected': true,
                    'fault_type': 'DISCONNECTED_WIRE',
                    'location': 'Row 12',
                    'possible_cause': 'Wire open',
                    'confidence': 0.91,
                    'bounding_box': {
                      'ymin': 0.2,
                      'xmin': 0.3,
                      'ymax': 0.4,
                      'xmax': 0.5,
                    }
                  })
                }
              ]
            }
          }
        ]
      });

      final mockClient = MockClient((request) async {
        expect(request.headers['x-goog-api-key'], 'test_key');
        return http.Response(mockResponse, 200);
      });

      final service = GeminiService(
        apiKey: 'test_key',
        httpClient: mockClient,
      );

      final result = await service.analyzeCircuitImage(Uint8List.fromList([1, 2, 3, 4]));

      expect(result.status, 'SUCCESS');
      expect(result.faultDetected, true);
      expect(result.faultType, 'DISCONNECTED_WIRE');
      expect(result.location, 'Row 12');
      expect(result.confidence, 0.91);
      expect(result.boundingBox, isNotNull);
    });

    test('Retries on HTTP 429 rate limit then recovers on success', () async {
      int attempts = 0;
      final mockResponse = jsonEncode({
        'candidates': [
          {
            'content': {
              'parts': [
                {
                  'text': jsonEncode({
                    'status': 'SUCCESS',
                    'fault_detected': false,
                    'fault_type': 'NONE',
                    'location': 'Loop intact',
                    'possible_cause': 'All pins seated',
                    'confidence': 0.98,
                  })
                }
              ]
            }
          }
        ]
      });

      final mockClient = MockClient((request) async {
        attempts++;
        if (attempts == 1) {
          return http.Response('Rate limit exceeded', 429);
        }
        return http.Response(mockResponse, 200);
      });

      final service = GeminiService(
        apiKey: 'test_key',
        maxRetries: 2,
        httpClient: mockClient,
      );

      final result = await service.analyzeCircuitImage(Uint8List.fromList([1, 2, 3]));

      expect(attempts, 2);
      expect(result.status, 'SUCCESS');
      expect(result.faultDetected, false);
    });

    test('Safely handles malformed non-JSON AI response with UNKNOWN status', () async {
      final mockResponse = jsonEncode({
        'candidates': [
          {
            'content': {
              'parts': [
                {'text': 'This is completely invalid non-JSON output from AI model.'}
              ]
            }
          }
        ]
      });

      final mockClient = MockClient((request) async {
        return http.Response(mockResponse, 200);
      });

      final service = GeminiService(
        apiKey: 'test_key',
        httpClient: mockClient,
      );

      final result = await service.analyzeCircuitImage(Uint8List.fromList([1, 2, 3]));

      expect(result.status, 'UNKNOWN');
      expect(result.possibleCause, contains('Failed to parse'));
    });
  });
}
