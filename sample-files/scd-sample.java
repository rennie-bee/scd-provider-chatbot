import java.util.*;

class Solution {
    List<Integer> solution(List<Integer> arr) {
        Map<Integer, Integer> freqMap = new HashMap<>();
        for(int num : arr) {
            freqMap.put(num, freqMap.getOrDefault(num, 0) + 1);
        }

        int MEX = 0;
        while(freqMap.containsKey(MEX)) {
            MEX++;
        }

        int N = arr.size();
        List<Integer> res = new ArrayList<>();
        int i = 0;
        while(i < N) {
            Set<Integer> set = new HashSet<>();
            int j = i;
            while(j < N) {
                if(arr.get(j) < MEX) {
                    set.add(arr.get(j));
                }
                if(set.size() == MEX) {
                    break;
                }
                j++;
            }
            res.add(MEX);
            while(i <= j) {
                int freq = freqMap.get(arr.get(i));
                freq--;
                if(freq == 0) {
                    freqMap.remove(arr.get(i));
                }
                else {
                    freqMap.put(arr.get(i), freq);
                }
                i++;
            }

            MEX = 0;
            while(freqMap.containsKey(MEX)) {
                MEX++;
            }
        }

        return res;
    }
}