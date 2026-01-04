#include "game_logic.h"

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <algorithm>

using namespace std;

const int WORD_LENGTH = 5;

// глобальні змінні
string TARGET_WORD = "";
bool HINT_USED = false;
string CURRENT_MODE = "EASY"; // за замовчуванням

// допоміжна функція для обрізання пробілів на початку/в кінці
static void trim_string(string &s) {
    auto not_space = [](unsigned char ch) { return !isspace(ch); };

    // обрізати пробіли зліва
    s.erase(s.begin(),
            find_if(s.begin(), s.end(), not_space));

    // якщо рядок не порожній – обрізати пробіли справа
    if (!s.empty()) {
        s.erase(
            find_if(s.rbegin(), s.rend(), not_space).base(),
            s.end()
        );
    }
}

// завантаження словника (англійські 5-літерні слова)
vector<string> load_dictionary(const string &filename) {
    vector<string> words;
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Cannot open dictionary file: " << filename << endl;
        return words;
    }

    string line;
    while (getline(file, line)) {
        // прибираємо пробіли/табуляції по краях
        trim_string(line);
        if (line.empty()) continue;

        transform(line.begin(), line.end(), line.begin(), ::toupper);

        if ((int)line.size() == WORD_LENGTH) {
            words.push_back(line);
        }
    }

    return words;
}

// словник для поточного режиму
vector<string> load_dictionary_for_mode(const string &mode) {
    if (mode == "HARD") {
        return load_dictionary("english_words_hard.txt");
    } else {
        return load_dictionary("english_words_easy.txt");
    }
}

// генерація фідбеку G/Y/B
string generate_feedback(const string &guess, const string &target) {
    int n = WORD_LENGTH;
    string res(n, 'B');
    vector<bool> used_target(n, false);

    // спочатку позначаємо зелені букви
    for (int i = 0; i < n; ++i) {
        if (guess[i] == target[i]) {
            res[i] = 'G';
            used_target[i] = true;
        }
    }

    // потім жовті (є в слові, але не на цьому місці)
    for (int i = 0; i < n; ++i) {
        if (res[i] == 'G') continue;
        for (int j = 0; j < n; ++j) {
            if (!used_target[j] && guess[i] == target[j]) {
                res[i] = 'Y';
                used_target[j] = true;
                break;
            }
        }
    }

    return res;
}

// підказка: одна випадкова позиція
string get_hint() {
    if (TARGET_WORD.empty()) return "-1 -";
    if (HINT_USED) return "-1 -";

    vector<int> positions;
    for (int i = 0; i < WORD_LENGTH; ++i) {
        positions.push_back(i);
    }
    int idx = rand() % positions.size();
    int pos = positions[idx];

    HINT_USED = true;

    string result = to_string(pos) + " " + string(1, TARGET_WORD[pos]);
    return result;
}

int main() {
    srand((unsigned)time(nullptr));

    string input;
    while (getline(cin, input)) {
        // прибрати тільки \r, якщо раптом є (Windows)
        input.erase(remove(input.begin(), input.end(), '\r'), input.end());

        // обрізати пробіли зліва/справа, але не всередині рядка
        trim_string(input);

        // перевести у верхній регістр
        transform(input.begin(), input.end(), input.begin(), ::toupper);

        // зміна режиму: MODE EASY / MODE HARD
        if (input.rfind("MODE ", 0) == 0) { // починається з "MODE "
            string mode = input.substr(5); // все після "MODE "
            trim_string(mode);             // на всяк випадок обрізати пробіли

            if (mode == "EASY" || mode == "HARD") {
                CURRENT_MODE = mode;
                cout << "MODE_OK " << CURRENT_MODE << endl;
            } else {
                cout << "MODE_ERR" << endl;
            }
            cout.flush();
        }
        else if (input == "START") {
            vector<string> dictionary = load_dictionary_for_mode(CURRENT_MODE);
            if (dictionary.empty()) {
                cerr << "Empty dictionary for mode: " << CURRENT_MODE << endl;
                cout << "ERROR: NO WORDS" << endl;
                cout.flush();
                continue;
            }

            int index = rand() % dictionary.size();
            TARGET_WORD = dictionary[index];
            HINT_USED = false;

            // debug у stderr
            cerr << "TARGET (" << CURRENT_MODE << "): " << TARGET_WORD << endl;

            cout << "READY " << WORD_LENGTH << endl;
            cout.flush();
        }
        else if (input == "HINT") {
            string hint = get_hint();
            cout << "HINT " << hint << endl;
            cout.flush();
        }
        else if ((int)input.size() == WORD_LENGTH) {
            if (TARGET_WORD.empty()) {
                cout << "ERROR: WORD NOT SET" << endl;
                cout.flush();
                continue;
            }

            string feedback = generate_feedback(input, TARGET_WORD);

            if (feedback == string(WORD_LENGTH, 'G')) {
                cout << "WIN " << feedback << endl;
            } else {
                cout << "FEEDBACK " << feedback << endl;
            }
            cout.flush();
        }
        else {
            cout << "INVALID" << endl;
            cout.flush();
        }
    }

    return 0;
}
